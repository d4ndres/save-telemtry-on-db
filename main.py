import time
from beamngpy import BeamNGpy
from beamngpy.sensors import Electrics
from dotenv import load_dotenv
import os
from pymongo import errors
from database.config_mongo import initialize_mongo, get_or_create_pilot, new_session, add_session_log
from pruebas.parking_lateral import create_scenario, SESSION_EJERCICIO  # Importamos SESSION_EJERCICIO

load_dotenv()

# SESSION
SESION_USERNAME = os.getenv("SESION_USERNAME")
SESION_IDENTIFICACION = os.getenv("SESION_IDENTIFICACION")
SESION_EMPRESA = os.getenv("SESION_EMPRESA")

pilot_session = None
current_session = None

def setup_mongo():
    global pilot_session
    try:
        initialize_mongo()
        pilot_session = get_or_create_pilot(SESION_IDENTIFICACION, SESION_USERNAME, SESION_EMPRESA)
    except errors.ServerSelectionTimeoutError as err:
        print("Error en la conexión con MongoDB, reintentando...")
        time.sleep(5)
        setup_mongo()

def setup_client():
    """Configura la conexión con BeamNG.tech."""
    client = BeamNGpy("localhost", 64890, home=r"C:\BeamNG.tech.v0.34.2.0")
    client.open()
    return client

session_vehiculo = "etk800"  # Definimos solo el vehículo, el nombre del ejercicio viene del módulo

def run_simulation(client, scenario, vehicle):
    """Carga el escenario, ejecuta la simulación y recopila la trayectoria del vehículo."""
    global current_session
    client.scenario.load(scenario)
    client.scenario.start()

    # Conectar el sensor y enfocar el vehículo
    vehicle.sensors.attach("electrics", Electrics())
    vehicle.connect(client)
    vehicle.focus()

    # Crear una nueva sesión en la base de datos
    current_session = new_session(pilot_session["_id"], {"exercise": SESSION_EJERCICIO, "vehicle": session_vehiculo})

    max_iter = 300
    try:
        for _ in range(max_iter):
            vehicle.sensors.poll()   # Actualiza los sensores
            state = vehicle.sensors["state"]
            sensors_electrics = vehicle.sensors["electrics"]
            
            # Guardar los datos de la sesión
            add_session_log(current_session.inserted_id, {
                "state": state,
                "sensors_electrics": sensors_electrics
            })

            client.control.step(15)
    except KeyboardInterrupt:
        print("Interrupción manual del bucle de telemetría.")
        client.disconnect()
    finally:
        client.scenario.stop()
        client.close()

def main():
    setup_mongo()
    client = setup_client()
    scenario, vehicle, cone_positions = create_scenario(client, session_vehiculo)  # Ya no pasamos session_ejercicio
    run_simulation(client, scenario, vehicle)

if __name__ == "__main__":
    main()

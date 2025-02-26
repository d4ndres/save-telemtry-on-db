import time
from shapely.geometry import Polygon, Point
import matplotlib.pyplot as plt
from beamngpy import BeamNGpy, Scenario, Vehicle, StaticObject, angle_to_quat
from beamngpy.sensors import Electrics
from dotenv import load_dotenv
import os
from pymongo import errors
from database.config_mongo import initialize_mongo, get_or_create_pilot, new_session, add_session_log
from pruebas import ejercicio_parqueo_conos  # Importar el módulo de pruebas

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
        print("Error en la conexión con mongo preparando para reconectar...")
        print(err)
        time.sleep(5)
        setup_mongo()

def setup_client():
    """Configura la conexión con BeamNG.tech."""
    client = BeamNGpy("localhost", 64890, home=r"D:\Formularacings\BeamNG.tech.v0.34.2.0")
    if not client.tech_enabled():
        client.open()
        time.sleep(10)
    return client

def run_simulation(client, scenario, vehicle, cones):
    """Carga el escenario, ejecuta la simulación y recopila la trayectoria del vehículo."""
    global current_session
    client.scenario.load(scenario)
    client.scenario.start()

    # Conectar el sensor y enfocar el vehículo
    vehicle.sensors.attach("electrics", Electrics())
    vehicle.connect(client)
    vehicle.focus()

    # Crear una nueva sesión en la base de datos
    current_session = new_session(pilot_session["_id"], {"exercise": scenario.name, "vehicle": vehicle.model})

    max_iter = 300
    try:
        for _ in range(max_iter):
            vehicle.sensors.poll()   # Actualiza los sensores
            state = vehicle.sensors["state"]
            sensors_electrics = vehicle.sensors["electrics"]
            

            # Detectar colisiones con los conos
            bbox = vehicle.get_bbox() 
            polygon_points = [
                (bbox['front_bottom_left'][0], bbox['front_bottom_left'][1]),
                (bbox['front_bottom_right'][0], bbox['front_bottom_right'][1]),
                (bbox['rear_bottom_right'][0], bbox['rear_bottom_right'][1]),
                (bbox['rear_bottom_left'][0], bbox['rear_bottom_left'][1])
            ]
            vehicle_polygon = Polygon(polygon_points)
            
            for cone in cones:
                cone_pos = (cone.pos[0], cone.pos[1])  # Solo tomamos X, Y
                cone_point = Point(cone_pos)

                # Verificar si el cono está dentro del polígono
                if vehicle_polygon.contains(cone_point):
                    print(f"Colisión detectada con {cone}")
                    

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
    scenario, vehicle, cones = ejercicio_parqueo_conos.create_scenario(client)  # Usar la función de prueba
    run_simulation(client, scenario, vehicle, cones)

if __name__ == "__main__":
    main()

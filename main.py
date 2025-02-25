import time
import matplotlib.pyplot as plt
from beamngpy import BeamNGpy, Scenario, Vehicle, StaticObject, angle_to_quat
from beamngpy.sensors import Electrics
from dotenv import load_dotenv
import os
from pymongo import errors
from database.config_mongo import initialize_mongo, get_or_create_user, new_session, add_session_log

load_dotenv()

# SESSION
SESION_USERNAME = os.getenv("SESION_USERNAME")
SESION_IDENTIFICACION = os.getenv("SESION_IDENTIFICACION")
SESION_EMPRESA = os.getenv("SESION_EMPRESA")

user_session = None
current_session = None

def setup_mongo():
    global user_session
    try:
        initialize_mongo()
        user_session = get_or_create_user(SESION_IDENTIFICACION, SESION_USERNAME, SESION_EMPRESA)
        
    except errors.ServerSelectionTimeoutError as err:
        print("Error en la conexión con mongo preparando para reconectar...")
        print(err)
        time.sleep(5)
        setup_mongo()

def setup_client():
    """Configura la conexión con BeamNG.tech."""
    client = BeamNGpy("localhost", 64890, home=r"D:\Formularacings\BeamNG.tech.v0.34.2.0")
    client.open()
    return client

session_ejercicio = "Ejercicio Parqueo - Conos"
session_vehiculo = "etk800"

def create_scenario(client):
    """Crea el escenario, agrega el vehículo a estacionar y los conos delimitadores."""
    scenario = Scenario("tech_ground", session_ejercicio,
                        description="El vehículo debe estacionarse en el área delimitada por conos.")
    # Vehículo a estacionar
    vehicle = Vehicle("cMiloVehicle", model=session_vehiculo,
                      part_config="vehicles/etk800/854_150d_M.pc",
                      color="red")
    # Posicionar el vehículo a la izquierda del área de parqueo
    scenario.add_vehicle(vehicle, pos=(15, 0, 0), rot_quat=(0, 0, -1, 1))

    # Coordenadas de conos proporcionadas
    cone_positions = [
        (20, -2),
        (20, 0),
        (20, 2),
        (27, 0),
        (27, -2),
        (27, 2),
        (30, 8),
        (20, 8),
        (25, 8),
        (25, -2),
        (35, -2),
        (40, -2),
        (35, 8),
        (40, 8),
        (15, 8),
        (15, -2)
    ]

    # Ordenar las posiciones de los conos por coordenada x y, luego por y
    cone_positions = sorted(cone_positions, key=lambda pos: (pos[0], pos[1]))

    # Agregar conos al escenario usando el modelo "cones"
    for i, pos in enumerate(cone_positions):
        cone = StaticObject(
            name=f"cone_{i}",
            pos=(pos[0], pos[1], 0),  # Agregar coordenada z
            rot_quat=angle_to_quat((0, 0, 55)),
            scale=(1, 1, 1),
            shape="/art/shapes/race/cone.dae",
        )
        scenario.add_object(cone)

    scenario.make(client)
    return scenario, vehicle, cone_positions

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
    current_session = new_session(user_session["_id"], {"exercise": session_ejercicio, "vehicle": session_vehiculo})

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
    scenario, vehicle, cone_positions = create_scenario(client)
    run_simulation(client, scenario, vehicle)

if __name__ == "__main__":
    main()

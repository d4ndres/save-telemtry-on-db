from beamngpy import Scenario, Vehicle, StaticObject, angle_to_quat

# Nombre del ejercicio
SESSION_EJERCICIO = "Ejercicio Parqueo - Conos"

def create_scenario(client, session_vehiculo):
    """Crea el escenario, agrega el vehículo a estacionar y las barreras delimitadoras."""
    scenario = Scenario("tech_ground", SESSION_EJERCICIO,
                        description="El vehículo debe estacionarse en el área delimitada por barreras.")

    # Vehículo a estacionar
    vehicle = Vehicle("cMiloVehicle", model=session_vehiculo,
                      part_config="vehicles/etk800/854_150d_M.pc",
                      color="black")

    # Posicionar el vehículo a la izquierda del área de parqueo
    scenario.add_vehicle(vehicle, pos=(15, 0, 0), rot_quat=(0, 0, -1, 1))

    # Coordenadas de barreras
    barrier_positions = [
        (20, -2), (20, 0), (20, 2), (27, 0), (27, -2), (27, 2),
        (30, 8), (20, 8), (25, 8), (25, -2), (35, -2), (40, -2),
        (35, 8), (40, 8), (15, 8), (15, -2)
    ]

    # Ordenar las posiciones de las barreras
    barrier_positions = sorted(barrier_positions, key=lambda pos: (pos[0], pos[1]))

    # Agregar barreras al escenario usando un modelo existente
    for i, pos in enumerate(barrier_positions):
        barrier = StaticObject(
            name=f"barrier_{i}",
            pos=(pos[0], pos[1], 0),  # Agregar coordenada z
            rot_quat=(0,0,-1,1),#angle_to_quat((0, 0, 0)),  # Orientación
            scale=(0.2, 0.4,0.6),  # Escala normal
            shape="/art/shapes/race/s_concrete_race_barrier.cdae"  # Modelo colisionable confirmado
            #shape="/art/shapes/race/cone.cdae"
        )
        scenario.add_object(barrier)

    scenario.make(client)
    return scenario, vehicle, barrier_positions

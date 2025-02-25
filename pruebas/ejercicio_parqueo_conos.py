from beamngpy import Scenario, Vehicle, StaticObject, angle_to_quat

def create_scenario(client):
    """Crea el escenario, agrega el vehículo a estacionar y los conos delimitadores."""
    session_ejercicio = "Ejercicio Parqueo - Conos"
    session_vehiculo = "etk800"
    
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
    return scenario, vehicle

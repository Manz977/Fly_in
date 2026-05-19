from algorithm.algorithm import PathFinder
from parser import Zone, Network
from typing import List, Optional


MAX_TURNS = 100

class Drone:
    def __init__(self, id: int, start_zone: Zone, path: List[str]) -> None:
        self.id = id
        self.current_position = start_zone.name
        self.path = path
        self.current_index = 0

    def get_current_position(self) -> str:
        return self.current_position

    def get_next_position(self) -> Optional[str]:
        next_position = self.current_index + 1
        if next_position < len(self.path):
            return self.path[next_position]
        else:
            return None

    def move(self) -> None:
        next_pos = self.get_next_position()
        if next_pos is not None:
            self.current_position = next_pos
            self.current_index += 1

class Simulator:
    def __init__(self, network: Network, pathfinder: PathFinder):
        if network.start_zone is None or network.end_zone is None:
            raise ValueError("Network must have start and end zones")
        self.network = network
        self.pathfinder = pathfinder
        self.zone_occupancy = {zone_name: 0 for zone_name in network.zones}
        self.drones = []
        self.link_occupancy = {}
        self.connection_map = {}

        for connection in network.connection:
            key = tuple(sorted([connection.zone1.name, connection.zone2.name]))
            self.link_occupancy[key] = 0
            self.connection_map[key] = connection
        path  = self.pathfinder.find_shortest_path(network.start_zone,
                                                   network.end_zone,
                                                   network)
        for drone_id in range(1, network.nb_drones + 1):
            drone = Drone(drone_id, network.start_zone, path)
            self.drones.append(drone)
        self.zone_occupancy[network.start_zone.name] = network.nb_drones

    def simulate_turn(self) -> None:
        for key in self.link_occupancy:
            self.link_occupancy[key] = 0
        movements = []
        for drone in self.drones:
            next_zone = drone.get_next_position()
            current_zone = drone.get_current_position()
            if next_zone is None:
                if self.zone_occupancy[current_zone] > 0:
                    self.zone_occupancy[current_zone] -= 1
                continue
            max_zone_capacity = self.network.zones[next_zone].max_drones
            connection_key = tuple(sorted([current_zone, next_zone]))
            connection = self.connection_map.get(connection_key)
            if connection is None:
                continue
            max_link_capacity = connection.max_link_capacity
            if self.zone_occupancy[next_zone] < max_zone_capacity and self.link_occupancy[connection_key] < max_link_capacity:
                drone.move()
                self.zone_occupancy[next_zone] += 1
                self.zone_occupancy[current_zone] -= 1
                self.link_occupancy[connection_key] += 1
                movements.append(f"D{drone.id}-{next_zone}")
        if movements:
            print(" ".join(movements))

    def all_drones_finished(self) -> bool:
        for drone in self.drones:
            if drone.get_next_position() is not None:
                return False
        return True

    def run_simulation(self) -> int:
        turn_counter = 0


        while not self.all_drones_finished() and turn_counter < MAX_TURNS:
            self.simulate_turn()
            turn_counter += 1
        if turn_counter >= MAX_TURNS:
            print(f"Warning: Simulation exceeded {MAX_TURNS} turns. Possible deadlock")
        return turn_counter

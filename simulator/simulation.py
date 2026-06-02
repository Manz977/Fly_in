from algorithm.algorithm import PathFinder
from parser import Zone, Network
from typing import Dict, List, Optional, Tuple, TypedDict


class TurnState(TypedDict):
    turn_number: int
    drone_positions: Dict[int, str]
    zone_occupancy: Dict[str, int]
    movements: List[str]
    turn_cost: int
    waiting_drones: List[Tuple[int, str, str]]


MAX_TURNS = 100


class Drone:
    """A single drone navigating a pre computed path through the network.

    Each drone holds a reference to its assigned path
    and tracks its current position as an index into that list.

    """

    def __init__(self, id: int, start_zone: Zone, path: List[str]) -> None:
        """Initialise a drone at the start of its path.

        """
        self.id = id
        self.current_position = start_zone.name
        self.path = path
        self.current_index = 0
        self.in_restricted_zone: bool = start_zone.zone_type == "restricted"

    def get_current_position(self) -> str:
        """Return the name of the zone the drone currently occupies.

        Returns:
            str: Current zone name.
        """
        return self.current_position

    def get_next_position(self) -> Optional[str]:
        """Return the name of the next zone on the drone's path, if any.

        Returns:
            Optional: The name of the next zone, or None if the
                drone has reached the end of its path.
        """
        next_position = self.current_index + 1
        if next_position < len(self.path):
            return self.path[next_position]
        else:
            return None

    def move(self) -> None:
        """Advance the drone one step along its path.
        """
        next_pos = self.get_next_position()
        if next_pos is not None:
            self.current_position = next_pos
            self.current_index += 1


class Simulator:
    """coordinate the turn by turn movement of all drones through the
    network.

    At construction time the shortest path is computed once, shared by all
    drones, and all drones are initialised at the start zone.  Each call to
    simulate_turn() attempts to advance every drone that has not yet
    arrived, respecting per zone capacity and per link capacity constraints.
    """

    def __init__(self, network: Network, pathfinder: PathFinder) -> None:
        """Set up the simulator, compute paths, and initialise all drones.

        All drones share the same shortest path computed between the
        network's start_zone and end_zone.

        """
        if network.start_zone is None or network.end_zone is None:
            raise ValueError("Network must have start and end zones")
        self.network = network
        self.pathfinder = pathfinder
        self.zone_occupancy = {zone_name: 0 for zone_name in network.zones}
        self.drones = []
        self.link_occupancy = {}
        self.connection_map = {}
        self.turn_history: List[TurnState] = []
        self.current_turn = 0

        for connection in network.connection:
            key = tuple(sorted([connection.zone1.name, connection.zone2.name]))
            self.link_occupancy[key] = 0
            self.connection_map[key] = connection

        path = self.pathfinder.find_shortest_path(
            network.start_zone, network.end_zone, network)
        for drone_id in range(1, network.nb_drones + 1):
            drone = Drone(drone_id, network.start_zone, path)
            self.drones.append(drone)
        self.zone_occupancy[network.start_zone.name] = network.nb_drones

        initial_state: TurnState = {
            'turn_number': 0,
            'drone_positions': {drone.id: drone.current_position
                                for drone in self.drones},
            'zone_occupancy': dict(self.zone_occupancy),
            'movements': [],
            'turn_cost': 0,
            'waiting_drones': [],
        }
        self.turn_history.append(initial_state)

    def simulate_turn(self, visual_mode: bool = False) -> int:
        """Advance the simulation by one turn and return its turn cost.

        For each drone that has not yet reached the end zone, the method
        attempts a move to the next zone on the drone's path.  A move
        succeeds only when both the destination zone and the connecting link
        have remaining capacity. Drones currently inside a restricted zone
        bypass capacity checks and are forced to exit immediately.
        """

        for key in self.link_occupancy:
            self.link_occupancy[key] = 0

        movements: List[str] = []
        entered_restricted = False
        waiting: List[Tuple[int, str, str]] = []

        for drone in self.drones:
            next_zone = drone.get_next_position()
            current_zone = drone.get_current_position()
            if next_zone is None:
                if self.zone_occupancy[current_zone] > 0:
                    self.zone_occupancy[current_zone] -= 1
                continue

            connection_key = tuple(sorted([current_zone, next_zone]))
            connection = self.connection_map.get(connection_key)
            if connection is None:
                waiting.append((drone.id, next_zone, "no_connection"))
                continue

            if drone.in_restricted_zone:
                drone.in_restricted_zone = False
                drone.move()
                self.zone_occupancy[next_zone] += 1
                self.zone_occupancy[current_zone] -= 1
                self.link_occupancy[connection_key] += 1
                movements.append(f"D{drone.id}-{next_zone}")
                if self.network.zones[next_zone].zone_type == "restricted":
                    drone.in_restricted_zone = True
                    entered_restricted = True
                continue

            max_zone_capacity = self.network.zones[next_zone].max_drones
            max_link_capacity = connection.max_link_capacity
            zone_ok = self.zone_occupancy[next_zone] < max_zone_capacity
            link_ok = self.link_occupancy[connection_key] < max_link_capacity

            moved = False
            if zone_ok and link_ok:
                drone.move()
                self.zone_occupancy[next_zone] += 1
                self.zone_occupancy[current_zone] -= 1
                self.link_occupancy[connection_key] += 1
                if self.network.zones[next_zone].zone_type == "restricted":
                    movements.append(f"D{drone.id}-{current_zone}-{next_zone}")
                    drone.in_restricted_zone = True
                    entered_restricted = True
                else:
                    movements.append(f"D{drone.id}-{next_zone}")
                moved = True

            if not moved:
                reason = "link_full" if zone_ok else "zone_full"
                waiting.append((drone.id, next_zone, reason))

        if not visual_mode:
            if movements:
                print(" ".join(movements))

        turn_cost = 2 if entered_restricted else 1
        turn_state: TurnState = {
            'turn_number': self.current_turn + 1,
            'drone_positions': {
                drone.id: drone.current_position for drone in self.drones
            },
            'zone_occupancy': dict(self.zone_occupancy),
            'movements': movements.copy(),
            'turn_cost': turn_cost,
            'waiting_drones': waiting.copy(),
        }
        self.turn_history.append(turn_state)
        self.current_turn += 1

        return turn_cost

    def all_drones_finished(self) -> bool:
        """Return whether every drone has reached the end of its path.
        """
        for drone in self.drones:
            if drone.get_next_position() is not None:
                return False
        return True

    def run_simulation(self, visual_mode: bool = False) -> int:
        """Run the simulation until all drones finish or the turn limit is
        hit."""
        turn_counter = 0

        while not self.all_drones_finished() and turn_counter < MAX_TURNS:
            turn_cost = self.simulate_turn(visual_mode)
            turn_counter += turn_cost

        if not visual_mode:
            if turn_counter >= MAX_TURNS:
                print(
                    f"Warning: Simulation exceeded {MAX_TURNS} turns. "
                    "Possible deadlock"
                )
        return turn_counter

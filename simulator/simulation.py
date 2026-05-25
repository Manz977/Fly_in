from algorithm.algorithm import PathFinder
from parser import Zone, Network
from typing import List, Optional


MAX_TURNS = 100


class Drone:
    """A single drone navigating a pre-computed path through the network.

    Each drone holds a reference to its assigned path (a list of zone names)
    and tracks its current position as an index into that list.

    Attributes:
        id (int): Unique numeric identifier for this drone.
        current_position (str): Name of the zone the drone currently
            occupies.
        path (List[str]): Ordered list of zone names from start to end.
        current_index (int): Index into ``path`` pointing to the drone's
            current position.
    """

    def __init__(self, id: int, start_zone: Zone, path: List[str]) -> None:
        """Initialise a drone at the start of its path.

        Args:
            id (int): Unique drone identifier.
            start_zone (Zone): The zone the drone starts in (must match
                ``path[0]``).
            path (List[str]): Full ordered path from start to end zone,
                as a list of zone names.
        """
        self.id = id
        self.current_position = start_zone.name
        self.path = path
        self.current_index = 0

    def get_current_position(self) -> str:
        """Return the name of the zone the drone currently occupies.

        Returns:
            str: Current zone name.
        """
        return self.current_position

    def get_next_position(self) -> Optional[str]:
        """Return the name of the next zone on the drone's path, if any.

        Returns:
            Optional[str]: The name of the next zone, or ``None`` if the
                drone has reached the end of its path.
        """
        next_position = self.current_index + 1
        if next_position < len(self.path):
            return self.path[next_position]
        else:
            return None

    def move(self) -> None:
        """Advance the drone one step along its path.

        If the drone is already at the end of its path, this is a no-op.
        """
        next_pos = self.get_next_position()
        if next_pos is not None:
            self.current_position = next_pos
            self.current_index += 1


class Simulator:
    """Orchestrates the turn-by-turn movement of all drones through the network.

    At construction time the shortest path is computed once (shared by all
    drones), and all drones are initialised at the start zone.  Each call to
    ``simulate_turn()`` attempts to advance every drone that has not yet
    arrived, respecting per-zone capacity and per-link capacity constraints.

    Attributes:
        network (Network): The drone delivery network being simulated.
        pathfinder (PathFinder): Path-finding engine used to compute routes.
        zone_occupancy (dict[str, int]): Current number of drones in each
            zone, keyed by zone name.
        drones (list[Drone]): All drone instances.
        link_occupancy (dict[tuple, int]): Current number of drones
            traversing each link this turn, keyed by a sorted
            ``(zone1_name, zone2_name)`` tuple.
        connection_map (dict[tuple, Connection]): Look-up from sorted zone
            name pair to the corresponding ``Connection`` object.
        turn_history (list[dict]): Snapshot of every turn's state for
            post-simulation playback by the visualiser.
        current_turn (int): 0-based index of the turn currently being
            simulated.
    """

    def __init__(self, network: Network, pathfinder: PathFinder) -> None:
        """Set up the simulator, compute paths, and initialise all drones.

        All drones share the same shortest path computed between the
        network's ``start_zone`` and ``end_zone``.

        Args:
            network (Network): The drone delivery network.
            pathfinder (PathFinder): Path-finding engine.

        Raises:
            ValueError: If the network does not have both a start and an
                end zone defined.
        """
        if network.start_zone is None or network.end_zone is None:
            raise ValueError("Network must have start and end zones")
        self.network = network
        self.pathfinder = pathfinder
        self.zone_occupancy = {zone_name: 0 for zone_name in network.zones}
        self.drones = []
        self.link_occupancy = {}
        self.connection_map = {}
        self.turn_history = []
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

    def simulate_turn(self, visual_mode: bool = False) -> None:
        """Advance the simulation by one turn.

        For each drone that has not yet reached the end zone, the method
        attempts a move to the next zone on the drone's path.  A move
        succeeds only when both the destination zone and the connecting link
        have remaining capacity.  Successfully moved drones update the
        occupancy counters accordingly.

        A snapshot of all drone positions, zone occupancy, and movement
        events is appended to ``turn_history`` regardless of whether any
        drones moved.

        Args:
            visual_mode (bool, optional): When ``True``, movement events
                are not printed to stdout (the visualiser handles display
                instead).  Defaults to ``False``.
        """
        # Reset per-turn link usage before computing new movements.
        for key in self.link_occupancy:
            self.link_occupancy[key] = 0

        movements = []
        for drone in self.drones:
            next_zone = drone.get_next_position()
            current_zone = drone.get_current_position()
            if next_zone is None:
                # Drone has finished; remove it from zone occupancy count.
                if self.zone_occupancy[current_zone] > 0:
                    self.zone_occupancy[current_zone] -= 1
                continue

            max_zone_capacity = self.network.zones[next_zone].max_drones
            connection_key = tuple(sorted([current_zone, next_zone]))
            connection = self.connection_map.get(connection_key)
            if connection is None:
                continue

            max_link_capacity = connection.max_link_capacity
            link_ok = self.link_occupancy[connection_key] < max_link_capacity
            if (self.zone_occupancy[next_zone] < max_zone_capacity
                    and link_ok):
                drone.move()
                self.zone_occupancy[next_zone] += 1
                self.zone_occupancy[current_zone] -= 1
                self.link_occupancy[connection_key] += 1
                movements.append(f"D{drone.id}-{next_zone}")

        if movements and not visual_mode:
            print(" ".join(movements))

        turn_state = {
            'turn_number': self.current_turn,
            'drone_positions': {
                drone.id: drone.current_position for drone in self.drones
            },
            'zone_occupancy': dict(self.zone_occupancy),
            'movements': movements.copy()
        }
        self.turn_history.append(turn_state)
        self.current_turn += 1

    def all_drones_finished(self) -> bool:
        """Return whether every drone has reached the end of its path.

        Returns:
            bool: ``True`` if all drones have no remaining moves;
                ``False`` if at least one drone still has further zones to
                traverse.
        """
        for drone in self.drones:
            if drone.get_next_position() is not None:
                return False
        return True

    def run_simulation(self, visual_mode: bool = False) -> int:
        """Run the simulation until all drones finish or the turn limit is hit.

        Calls ``simulate_turn()`` repeatedly until either
        ``all_drones_finished()`` returns ``True`` or ``MAX_TURNS`` is
        reached (a safety guard against deadlocks).

        Args:
            visual_mode (bool, optional): Passed through to
                ``simulate_turn()``.  When ``True``, per-turn movement
                output is suppressed.  Defaults to ``False``.

        Returns:
            int: Total number of turns executed.
        """
        turn_counter = 0

        while not self.all_drones_finished() and turn_counter < MAX_TURNS:
            self.simulate_turn(visual_mode)
            turn_counter += 1

        if not visual_mode:
            if turn_counter >= MAX_TURNS:
                print(
                    f"Warning: Simulation exceeded {MAX_TURNS} turns. "
                    "Possible deadlock"
                )
        return turn_counter

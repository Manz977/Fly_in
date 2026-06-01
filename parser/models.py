from typing import List, Optional


class Zone:
    """
    A node in the drone delivery network (called a hub).

    Attributes:
        name: Unique identifier for the zone.
        x: x coordinate used for layout and visualisation.
        y: y coordinate used for layout and visualisation.
    """

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        zone_type: str = "normal",
        max_drones: int = 1,
        color: str = "none",
    ) -> None:

        allowed_zones: List[str] = [
            "normal",
            "blocked",
            "restricted",
            "priority",
        ]
        if zone_type not in allowed_zones:
            raise ValueError(f"Invalid zone type: {zone_type}")
        if max_drones < 1:
            raise ValueError("Capacity must be a positive integer")

        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.max_drones = max_drones
        self.color = color


class Connection:
    """A bidirectional edge linking two zones in the network.

    Connections are symmetric: traffic may flow in either direction, but
    the total simultaneous drone traffic on the link is specified by
    max_link_capacity.

    """

    def __init__(
        self,
        zone1: Zone,
        zone2: Zone,
        max_link_capacity: int = 1,
    ) -> None:
        """Initialise a connection between two zones with a capacity limit.

        Args:
            zone1: First endpoint zone.
            zone2: Second endpoint zone.
            max_link_capacity: Maximum number of drones
                allowed to use this link per turn. Must be more then 1.
        """
        if max_link_capacity < 1:
            raise ValueError(
                "max link capacity must be positive integer"
            )

        self.zone1 = zone1
        self.zone2 = zone2
        self.max_link_capacity = max_link_capacity


def same_connection(a: Connection, b: Connection) -> bool:
    """
    Return whether two connections link the same pair of zones.

    The check is order independent: a connection from zone A to zone B is
    considered the same as one from zone B to zone A.

    """
    return {a.zone1, a.zone2} == {b.zone1, b.zone2}


class Network:
    """The drone delivery network graph, composed of zones and connections.

    The network is stored internally as both a flat zone/connection registry
    and an adjacency list to support efficient neighbour look ups.

    Attributes:
        nb_drones: Total number of drones operating in this network.
        zones: Mapping of zone name.
        connection: All connections in the network.
        adj_list: Adjacency list mapping each zone
            name to its directly connected neighbour zones.
        start_zone: The zone from which all drones depart.
        end_zone: The zone all drones are trying to reach.
    """

    def __init__(self, nb_drones: int) -> None:
        """
        Initialise an empty network with a fixed drone fleet size.
        """
        if nb_drones < 1:
            raise ValueError("Number of drones should be a positive number")
        self.nb_drones = nb_drones
        self.zones: dict[str, Zone] = {}
        self.connection: list[Connection] = []
        self.adj_list: dict[str, list[Zone]] = {}
        self.start_zone: Optional[Zone] = None
        self.end_zone: Optional[Zone] = None

    def add_zone(self, zone: Zone) -> None:
        """
        Register a zone in the network.

        Raises:
            ValueError: If a zone with the same name already exists.
        """
        if zone.name in self.zones:
            raise ValueError(f"Duplicate {zone.name} detected")
        self.zones[zone.name] = zone
        self.adj_list[zone.name] = []

    def add_connection(self, connection: Connection) -> None:
        """
        Register a connection and update the adjacency list for both endpoints.

        Raises:
            ValueError: If an identical connection
                already exists in the network.
        """
        for existing_conn in self.connection:
            if same_connection(existing_conn, connection):
                raise ValueError("duplicate found for connections")
        self.connection.append(connection)
        z1_name = connection.zone1.name
        z2_name = connection.zone2.name

        self.adj_list[z1_name].append(connection.zone2)
        self.adj_list[z2_name].append(connection.zone1)

    def set_start(self, zone: Zone) -> None:
        """
        Designate a zone as the network's start zone.

        Raises:
            ValueError: If a start zone has already been set.
        """
        if self.start_zone is not None:
            raise ValueError("Start zone already defined")
        self.start_zone = zone

    def set_end(self, zone: Zone) -> None:
        """
        Designate a zone as the network's end zone.

        Raises:
            ValueError: If an end zone has already been set.
        """
        if self.end_zone is not None:
            raise ValueError("End zone already defined")
        self.end_zone = zone

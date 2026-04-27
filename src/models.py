from typing import List, Optional

class Zone:
    """
    Represents the hub in the drone network.

    Attributes:
        name (str): Uniqque identifier for the zone.
        x (int): X-coordinate.
        y (int): Y-coordinate.
        zone_type (str): Type of zone (normal, blocked, restricted, priority).
        max_drones (int): Maximum occupancy capacity.
        color (str): Vsual representation color.
    """
    def __init__(self,
                 name: str,
                 x: int,
                 y: int,
                 zone_type: str= "normal",
                 max_drones: int= 1,
                 color: str= "none" ) -> None:
        allowed_zones: List[str] = ["normal", "blocked", "restricted", "priority"]
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
    """
    Represents a bidirectional link between two zones.

    Attributes:
        zone1 Zone: The first endpoint zone.
        zone2 Zone: The second endpoint zone.
        max_link_capacity int: Maximum number of drones allowed on the link.
    """
    def __init__(self, zone1: Zone, zone2: Zone, max_link_capacity: int = 1) -> None:
        """
        Initialize a connection between two zones with a capacity constraint.

        Args:
            zone1 Zone: The first endpoint zone.
            zone2 Zone: The second endpoint zone.
            max_link_capacity (int, optional): Maximum number of drones allowed
                on the link. Defaults to 1.

        Raises:
            ValueError: If `max_link_capacity` is less than 1.
        """
        if max_link_capacity < 1:
            raise ValueError("max link capacity must be positive integer")

        self.zone1 = zone1
        self.zone2 = zone2
        self.max_link_capacity = max_link_capacity

def same_connection(a: Connection, b: Connection) -> bool:
    """
    Check whether two connections link the same pair of zones.

    Args:
        a (Connection): First connection to compare.
        b (Connection): Second connection to compare.

    Returns:
        bool: True if both connections connect the same zones, regardless of
            order; otherwise False.
    """
    return {a.zone1, a.zone2} == {b.zone1, b.zone2}

class Network:
    """
    Represents a drone delivery network with zones and connections.

    Attributes:
        nb_drones (int): Total number of drones available in the network.
        zones (dict[str, Zone]): Mapping of zone names to Zone objects.
        connection (list[Connection]): List of connections between zones.
        start_zone (Optional[Zone]): Designated start zone.
        end_zone (Optional[Zone]): Designated end zone.
    """
    def __init__(self, nb_drones: int)-> None:
        """
        Initialize a network with a fixed number of drones.

        Args:
            nb_drones (int): Total number of drones in the network.

        Raises:
            ValueError: If `nb_drones` is less than 1.
        """
        if nb_drones < 1:
            raise ValueError("Number of drones should be a positive number")
        self.nb_drones = nb_drones
        self.zones = {}
        self.connection = []
        self.start_zone: Optional[Zone] = None
        self.end_zone: Optional[Zone] = None

    def add_zone(self, zone: Zone) -> None:
        """
        Add a new zone to the network.

        Args:
            zone (Zone): Zone to add.

        Raises:
            ValueError: If a zone with the same name already exists.
        """
        if zone.name in self.zones:
            raise ValueError(f"Duplicate {zone.name} detected")
        self.zones[zone.name] = zone

    def add_connection(self, connection: Connection) -> None:
        """
        Add a connection to the network.

        Args:
            connection (Connection): Connection to add.

        Raises:
            ValueError: If a duplicate connection already exists.
        """
        for existing_conn in self.connection:
            if same_connection(existing_conn, connection):
                raise ValueError("duplicate found for connections")
        self.connection.append(connection)


    def set_start(self, zone: Zone) -> None:
        """
        Set the start zone for the network.

        Args:
            zone (Zone): Zone to set as the start.

        Raises:
            ValueError: If the start zone is already defined.
        """
        if self.start_zone is not None:
            raise ValueError("Start zone already defined")
        self.start_zone = zone

    def set_end(self, zone: Zone) -> None:
        """
        Set the end zone for the network.

        Args:
            zone (Zone): Zone to set as the end.

        Raises:
            ValueError: If the end zone is already defined.
        """
        if self.end_zone is not None:
            raise ValueError("Start zone already defined")
        self.end_zone = zone

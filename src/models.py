from typing import List

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

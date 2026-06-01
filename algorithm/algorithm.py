from parser.models import Network, Zone
from typing import List, Optional
import heapq


class PathFinder:
    """Computes shortest paths through a drone delivery network.

    Uses Dijkstra's algorithm with zone type based traversal costs to find
    the optimal route from a start zone to an end zone while avoiding
    blocked zones.
    """

    def find_shortest_path(
        self, start: Zone, end: Zone, network: Network
    ) -> List[str]:
        """Find the shortest lowest cost path between two zones.

        Applies Dijkstra's algorithm over the network graph. Edge cost is
        determined solely by the destination zone type.

        """
        if start is None or end is None:
            raise ValueError("Start and end zones cannot be None")
        if network is None:
            raise ValueError("Network cannot be None")
        if start.name == end.name:
            return [start.name]

        distances = {
            name: float('inf') for name in network.zones
        }
        distances[start.name] = 0

        parent: dict[str, Optional[str]] = {
            name: None for name in network.zones
        }
        parent[start.name] = None
        visited = set()

        priority_queue = [(0.0, start.name)]

        while priority_queue:
            distance, current_zone = heapq.heappop(priority_queue)
            if current_zone in visited:
                continue
            visited.add(current_zone)

            for connection in network.connection:
                if connection.zone1.name == current_zone:
                    neighbor = connection.zone2
                elif connection.zone2.name == current_zone:
                    neighbor = connection.zone1
                else:
                    continue

                zone_cost = {
                    "normal": 1,
                    "blocked": float('inf'),
                    "restricted": 2,
                    "priority": 1,
                }
                new_distance = (
                    distances[current_zone]
                    + zone_cost[neighbor.zone_type]
                )
                if new_distance < distances[neighbor.name]:
                    distances[neighbor.name] = new_distance
                    parent[neighbor.name] = current_zone
                    heapq.heappush(
                        priority_queue, (new_distance, neighbor.name)
                    )

        if end.name not in visited:
            raise ValueError(
                f"No path exists from {start.name} to {end.name}"
            )

        path: list[str] = []
        current: str | None = end.name
        while current is not None:
            path.append(current)
            current = parent[current]
        path.reverse()
        return path

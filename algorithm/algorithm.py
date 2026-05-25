from parser.models import Network, Zone
from typing import List, Optional
import heapq


class PathFinder:
    """Computes shortest paths through a drone delivery network.

    Uses Dijkstra's algorithm with zone-type-based traversal costs to find
    the optimal route from a start zone to an end zone while avoiding
    blocked zones.
    """

    def find_shortest_path(
        self, start: Zone, end: Zone, network: Network
    ) -> List[str]:
        """Find the shortest (lowest-cost) path between two zones.

        Applies Dijkstra's algorithm over the network graph.  Edge cost is
        determined solely by the *destination* zone type:

        - ``normal``   → cost 1
        - ``priority`` → cost 1
        - ``restricted`` → cost 2
        - ``blocked``  → cost ∞ (effectively impassable)

        Args:
            start (Zone): The zone from which path-finding begins.
            end (Zone): The target zone to reach.
            network (Network): The drone network containing zones and
                connections.

        Returns:
            List[str]: An ordered list of zone names representing the path
                from ``start`` to ``end`` (both inclusive).  If
                ``start == end`` a single-element list is returned.

        Raises:
            ValueError: If ``start``, ``end``, or ``network`` is ``None``.
            ValueError: If no path exists between ``start`` and ``end``
                (e.g. the destination is unreachable due to blocked zones).
        """
        if start is None or end is None:
            raise ValueError("Start and end zones cannot be None")
        if network is None:
            raise ValueError("Network cannot be None")
        if start.name == end.name:
            return [start.name]

        # Map each zone name to its best-known cumulative travel cost.
        distances = {
            name: float('inf') for name in network.zones
        }
        distances[start.name] = 0

        # Predecessor map used to reconstruct the path after the search.
        parent: dict[str, Optional[str]] = {
            name: None for name in network.zones
        }
        parent[start.name] = None
        visited = set()

        # Min-heap entries are (cost, zone_name) tuples.
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

        # Reconstruct path by walking the predecessor chain in reverse.
        path = []
        current = end.name
        while current is not None:
            path.append(current)
            current = parent[current]
        path.reverse()
        return path

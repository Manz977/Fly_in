from parser.models import Network, Zone
from typing import List
import  heapq

"""
    1. Initialize:
   - distances = { all zones: infinity }
   - distances[start] = 0
   - parent = { all zones: None }  // Track where we came from
   - visited = empty set
   - priority_queue = [(0, start)]

2. While priority_queue is not empty:
   a. Pop zone with smallest distance
   b. If already visited, skip
   c. Mark as visited
   d. For each neighbor of this zone:
      - Calculate new distance = distances[current] + cost_to_neighbor
      - If new distance < distances[neighbor]:
        - Update distances[neighbor]
        - Update parent[neighbor] = current  // Remember we came from current
        - Add (new_distance, neighbor) to priority_queue

3. After loop:
   - Start at end zone
   - Follow parent pointers back to start
   - Reverse to get path from start to end
   - Return path

    """
class PathFinder:
    def find_shortest_path(self, start, end, network) -> List:
        # Stores the current known distance to each zone
        distances = {name: float('inf') for name in network.zones}
        distances[start] = 0
        parent = {name: None for name in network.zones}
        visited = set()
        # Stores zones waiting to be explored
        priority_queue = [(0, start)]

        while priority_queue:
            distance, current_zone = heapq.heappop(priority_queue)
            if current_zone in visited:
                continue
            visited.add(current_zone)


import sys
from parser.parser import MapParser
from algorithm.algorithm import PathFinder
from pathlib import Path
from simulator import Simulator
if len(sys.argv) > 1:
    path_to_the_file = Path(sys.argv[1])
else:
    BASE_DIR = Path(__file__).resolve().parent
    path_to_the_file = BASE_DIR / "maps" / "hard" / "03_ultimate_challenge.txt"

parser = MapParser(path_to_the_file)
network = parser.parse()
pathfinder = PathFinder()
#if network.start_zone is None or network.end_zone is None:
#    raise ValueError("Network must have start and end zones")
#path = pathfinder.find_shortest_path(
#    network.start_zone,
#    network.end_zone,
#    network
#)

simulator = Simulator(network, pathfinder)
turns = simulator.run_simulation()
print(f"\nSimulation completed in {turns} Turns")

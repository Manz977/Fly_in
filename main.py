import sys
from parser.parser import MapParser
from algorithm.algorithm import PathFinder
from pathlib import Path
from simulator import Simulator
from visual import Visualizer
"""
Entry point for the Fly_in pathfinding simulation.

Parses a map file defaulting to maps/hard/03_ultimate_challenge.txt if no
argument is provided, runs the pathfinding simulation, then launches the
visual playback. Prints the total number of turns on exit.

"""

if len(sys.argv) > 1:
    path_to_the_file = Path(sys.argv[1])
else:
    BASE_DIR = Path(__file__).resolve().parent
    path_to_the_file = BASE_DIR / "maps" / "hard" / "03_ultimate_challenge.txt"

parser = MapParser(path_to_the_file)
network = parser.parse()
if network.start_zone is None or network.end_zone is None:
    raise ValueError("Network must have start and end zones")


pathfinder = PathFinder()
simulator = Simulator(network, pathfinder)
turns = simulator.run_simulation(visual_mode=False)

visualizer = Visualizer(network, simulator.turn_history)

visualizer.run()
print(f"\nSimulation completed in {turns} Turns")

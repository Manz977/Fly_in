#!/usr/bin/env python3
"""Quick test script for the MapParser."""

from pathlib import Path
from src.parser import parse_map

# Test with easy map
easy_map = Path("maps/easy/01_linear_path.txt")
print(f"Testing: {easy_map}")
network = parse_map(easy_map)
print(f"  Drones: {network.nb_drones}")
print(f"  Zones: {len(network.zones)}")
print(f"  Connections: {len(network.connection)}")
print(f"  Start: {network.start_zone.name if network.start_zone else 'None'}")
print(f"  End: {network.end_zone.name if network.end_zone else 'None'}")
print()

# Test with medium map
medium_map = Path("maps/medium/01_dead_end_trap.txt")
print(f"Testing: {medium_map}")
network = parse_map(medium_map)
print(f"  Drones: {network.nb_drones}")
print(f"  Zones: {len(network.zones)}")
print(f"  Connections: {len(network.connection)}")
print(f"  Start: {network.start_zone.name if network.start_zone else 'None'}")
print(f"  End: {network.end_zone.name if network.end_zone else 'None'}")
print()

# Test with challenger map
challenger_map = Path("maps/challenger/01_the_impossible_dream.txt")
print(f"Testing: {challenger_map}")
network = parse_map(challenger_map)
print(f"  Drones: {network.nb_drones}")
print(f"  Zones: {len(network.zones)}")
print(f"  Connections: {len(network.connection)}")
print(f"  Start: {network.start_zone.name if network.start_zone else 'None'}")
print(f"  End: {network.end_zone.name if network.end_zone else 'None'}")
print()

print("✓ All tests passed!")

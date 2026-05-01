
from typing import Optional
from models import Network, Zone
from pathlib import Path
import re
BASE_DIR = Path(__file__).resolve().parent
path_to_the_file = BASE_DIR.parent / "maps" / "challenger" / "01_the_impossible_dream.txt"


def parse_map(path: Path) -> Network:
    network: Optional[Network] = None

    with open(path, "r") as file:
        for line_num, line in enumerate(file, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            if network is None:
                if not stripped.startswith("nb_drones:"):
                    msg = (
                        f"Line {line_num}: First data line must be "
                        "'nb_drones:'"
                    )
                    raise ValueError(msg)
                try:
                    parts = stripped.split(":")

                    if len(parts) < 2:
                        raise ValueError("Missing value after 'nb_drones:'")
                    num_dr = int(parts[1].strip())
                    network = Network(num_dr)
                except ValueError as e:
                    msg = f"Line {line_num}: Invalid drone count - {e}"
                    raise ValueError(msg)
                continue

            if stripped.startswith("start_hub:"):
                if network is None:
                    msg = "found a start_hub before defining nb_drones"
                    raise ValueError(msg)
                pattern = r"start_hub:\s+(\w+)\s+(\d+)\s+(\d+)"
                match = re.search(pattern, stripped)
                if match:
                    name = match.group(1)
                    x_coordinates = match.group(2)
                    y_coordinates = match.group(3)
                    print(name, x_coordinates, y_coordinates)
                #if len(parts) < 3:
                #    raise ValueError(
                #        f"Line {line_num}:Hub needs a name and two coordinates"
                #    )
                    try:
                        label = name
                        x = int(x_coordinates)
                        y = int(y_coordinates)
                        print(name, x, y)
                        new_zone = Zone(label, x, y)
                        network.add_zone(new_zone)
                        network.set_start(new_zone)

                    except ValueError:
                        msg = f"Line {line_num}: Coordinates must be integers"
                        raise ValueError(msg)

            if stripped.startswith("end_hub:"):
                if network is None:
                    msg = "Found an end_hub befoe defining nb_drones"
                    raise ValueError(msg)
                label_end, content_end = stripped.split(":", 1)
                parts = content_end.strip().split()

                if len(parts) < 3:
                    raise ValueError(
                        f"Line {line_num}: Hub need a name and two coordinates"
                    )
                try:
                    name = parts[0]
                    x = int(parts[1])
                    y = int(parts[2])

                    new_zone = Zone(name, x, y)
                    network.add_zone(new_zone)
                    network.set_end(new_zone)

                except ValueError:
                    msg = f"Line {line_num}: Coordinates must be integers"
                    raise ValueError(msg)
    if network is None:
        raise ValueError("The file is empty or missing 'nb_drones:'")
    return network


parse_map(path_to_the_file)

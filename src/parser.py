
from typing import Optional
from models import Network, Zone
from pathlib import Path
import re
BASE_DIR = Path(__file__).resolve().parent
path_to_the_file = BASE_DIR.parent / "maps" / "challenger" / "01_the_impossible_dream.txt"

class MapParser:

    def __init__(self, path: Path) -> None:
        self.path = path
        self.network: Optional[Network] = None
    def parse(self):
        if self.network is not None:
            raise RuntimeError("Network has already been parsed fpr this instance!")
        self.path
        self.network
        with open(self.path, "r") as file:
            for line_num, line in enumerate(file, 1):
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped.startswith("#start_hub:"):
                        stripped = stripped[1:]
                elif stripped.startswith("#"):
                    continue

                if self.network is None:
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
                        print(num_dr)
                        self.network = Network(num_dr)
                    except ValueError as e:
                        msg = f"Line {line_num}: Invalid drone count - {e}"
                        raise ValueError(msg)
                    continue

                if stripped.startswith("start_hub:"):
                    if self.network is None:
                        msg = "found a start_hub before defining nb_drones"
                        raise ValueError(msg)

                    pattern = r"start_hub:\s+(\w+)\s+(\d+)\s+(\d+)\s*(?:\[(.*)\])?"
                    match = re.search(pattern, stripped)
                    #if len(match) < 3:
                    #    raise ValueError(
                    #        f"Line {line_num}:Hub needs a name and two coordinates"
                    #    )
                    if match:
                        name = match.group(1)
                        x_coordinates = match.group(2)
                        y_coordinates = match.group(3)
                        metadata = match.group(4)
                        print(metadata)
                        try:
                            label = name
                            x = int(x_coordinates)
                            y = int(y_coordinates)
                            print(name, x, y)
                            new_zone = Zone(label, x, y)
                            self.network.add_zone(new_zone)
                            self.network.set_start(new_zone)

                        except ValueError:
                            msg = f"Line {line_num}: Coordinates must be integers"
                            raise ValueError(msg)

                if stripped.startswith("end_hub:"):
                    if self.network is None:
                        msg = "Found an end_hub befoe defining nb_drones"
                        raise ValueError(msg)
                    end_pattern = r"end_hub:\s+(\w+)\s+(\d+)\s+(\d+)\s*(?:\[(.*)\])?"
                    end_match = re.search(end_pattern, stripped)
                    #label_end, content_end = stripped.split(":", 1)
                    #parts = content_end.strip().split()
                    if end_match:
                        name_end = end_match.group(1)
                        coordinates_x_end = end_match.group(2)
                        coordinates_y_end = end_match.group(3)
                        metdata_end = end_match.group(4)
                        print(f"metadta for the end hub: {metdata_end}")
                    try:
                        name = name_end
                        x = int(coordinates_x_end)
                        y = int(coordinates_y_end)
                        new_zone = Zone(name_end, x, y)
                        self.network.add_zone(new_zone)
                        self.network.set_end(new_zone)

                    except ValueError:
                        msg = f"Line {line_num}: Coordinates must be integers"
                        raise ValueError(msg)
        if self.network is None:
            raise ValueError("The file is empty or missing 'nb_drones:'")
        return self.network


my_parser = MapParser(path_to_the_file)
built_network = my_parser.parse()

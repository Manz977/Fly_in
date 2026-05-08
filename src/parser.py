from typing import Optional, Dict
from models import Network, Zone, Connection
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent
path_to_the_file = (
    BASE_DIR.parent / "maps" / "challenger" / "01_the_impossible_dream.txt"
)


class MapParser:

    def __init__(self, path: Path) -> None:
        self.path = path
        self.network: Optional[Network] = None
        self.zones: Dict[str, Zone] = {}

    def _parse_metadata(self, metadata_string: str) -> Dict[str, str]:
        if metadata_string is None:
            return {}
        datas = metadata_string.split()

        data_dict = {
            data.split('=', 1)[0]: data.split('=', 1)[1]
            for data in datas
        }
        return data_dict

    def _parse_hub(
        self, hub_type: str, stripped_line: str, line_num: int
    ) -> None:
        pattern = (
            rf"{hub_type}\s+(\w+)\s+(\d+)\s+(\d+)\s*(?:\[([^\]]*)\])?"
        )
        match = re.search(pattern, stripped_line)
        if match:
            name = match.group(1)
            val1 = int(match.group(2))
            val2 = int(match.group(3))
            metadata_str = match.group(4)
            metadata_dict = {}

            zone_type = "normal"
            color = "none"
            max_drones = 1
            if metadata_str:
                metadata_dict = self._parse_metadata(metadata_str)
                zone_type = metadata_dict.get("zone", "normal")
                color = metadata_dict.get("color", "none")
                raw_value = metadata_dict.get("max_drones", "1")
                max_drones = int(raw_value)

            if hub_type == "start_hub":
                if self.network is None:
                    msg = "found a start_hub before defining nb_drones"
                    raise ValueError(msg)
                try:
                    new_zone = Zone(
                        name, val1, val2, zone_type, max_drones, color
                    )
                    self.network.add_zone(new_zone)
                    self.network.set_start(new_zone)
                    self.zones[name] = new_zone
                except ValueError:
                    msg = f"Line {line_num}: Coordinates must be integers"
                    raise ValueError(msg)

            elif hub_type == "end_hub":
                if self.network is None:
                    msg = "Found an end_hub befoe defining nb_drones"
                    raise ValueError(msg)

                try:
                    end_hub = Zone(
                        name, val1, val2, zone_type, max_drones, color
                    )
                    self.network.set_end(end_hub)
                    self.zones[name] = end_hub

                except ValueError:
                    msg = f"Line {line_num}: Coordinates must be integers"
                    raise ValueError(msg)

            elif hub_type == "hub":
                if self.network is None:
                    msg = "Found an end_hub befoe defining nb_drones"
                    raise ValueError(msg)
                try:
                    new_hub = Zone(
                        name, val1, val2, zone_type, max_drones, color
                    )
                    self.network.add_zone(new_hub)
                    self.zones[name] = new_hub

                except ValueError:
                    msg = f"Line {line_num}: Coordinates must be integers"
                    raise ValueError(msg)

    def parse(self):
        if self.network is not None:
            msg = "Network has already been parsed fpr this instance!"
            raise RuntimeError(msg)
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
                            raise ValueError(
                                "Missing value after 'nb_drones:'"
                            )
                        num_dr = int(parts[1].strip())
                        self.network = Network(num_dr)
                    except ValueError as e:
                        msg = f"Line {line_num}: Invalid drone count - {e}"
                        raise ValueError(msg)
                    continue

                if stripped.startswith("connection:"):
                    connections = r"connection:\s+([\w-]+)\s*(?:\[([^\]]*)\])?"
                    match = re.search(connections, stripped)
                    if match:
                        raw_id = match.group(1)
                        metadata_str = match.group(2)
                        val1, val2 = raw_id.split("-")

                        zone1 = self.zones.get(val1)
                        zone2 = self.zones.get(val2)

                        if zone1 and zone2:
                            capacity = 1
                            if metadata_str:
                                meta_dict = self._parse_metadata(
                                    metadata_str
                                )
                                try:
                                    capacity = int(
                                        meta_dict.get("max_link_capacity", 1)
                                    )
                                except ValueError:
                                    capacity = 1
                            new_conn = Connection(zone1, zone2, capacity)
                            self.network.add_connection(new_conn)
                        else:
                            msg = (
                                f"Line {line_num}: Connection refers to "
                                "unknown zones"
                            )
                            raise ValueError(msg)
                    continue

                if stripped.startswith("start_hub:"):
                    self._parse_hub("start_hub", stripped, line_num)
                    continue
                elif stripped.startswith("end_hub:"):
                    self._parse_hub("end_hub", stripped, line_num)
                    continue
                elif stripped.startswith("hub:"):
                    self._parse_hub("hub", stripped, line_num)
                    continue

        if self.network is None:
            raise ValueError("The file is empty or missing 'nb_drones:'")
        return self.network


if __name__ == "__main__":
    my_parser = MapParser(path_to_the_file)
    built_network = my_parser.parse()

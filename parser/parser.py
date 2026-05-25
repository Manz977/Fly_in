from typing import Optional, Dict
from .models import Network, Zone, Connection
from pathlib import Path
import re


BASE_DIR = Path(__file__).resolve().parent
path_to_the_file = (
    BASE_DIR.parent / "maps" / "hard" / "01_maze_nightmare.txt"
)


class MapParser:
    """Parse a ``.txt`` map file into a ``Network`` object.

    Map files follow a custom line-oriented format::

        nb_drones: <count>
        start_hub: <name> <x> <y> [key=value ...]
        end_hub:   <name> <x> <y> [key=value ...]
        hub:       <name> <x> <y> [key=value ...]
        connection: <name1>-<name2> [key=value ...]

    Lines beginning with ``#`` are treated as comments and skipped, with
    the special exception that ``#start_hub:`` lines have their leading
    ``#`` stripped before parsing (used in some map files to mark the start
    hub inline with a comment prefix).

    Attributes:
        path (Path): Absolute path to the map file.
        network (Optional[Network]): The network built during parsing.
            ``None`` until ``parse()`` is called.
        zones (Dict[str, Zone]): Running registry of parsed zones, used to
            resolve zone references in ``connection:`` lines.
    """

    def __init__(self, path: Path) -> None:
        """Initialise the parser with the path to a map file.

        Args:
            path (Path): Path to the ``.txt`` map file to parse.
        """
        self.path = path
        self.network: Optional[Network] = None
        self.zones: Dict[str, Zone] = {}

    def _parse_metadata(self, metadata_string: str) -> Dict[str, str]:
        """Parse a bracket-enclosed metadata string into a key/value dict.

        Metadata is encoded as space-separated ``key=value`` pairs that
        appear inside ``[...]`` in hub and connection lines, e.g.::

            [zone=restricted max_drones=3 color=red]

        Args:
            metadata_string (str): The raw content between ``[`` and ``]``,
                or ``None`` if the bracket section was absent.

        Returns:
            Dict[str, str]: Mapping of metadata keys to their string values.
                Returns an empty dict if ``metadata_string`` is ``None``.
        """
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
        """Parse a single hub line and register the resulting zone.

        Handles the three hub keywords – ``start_hub``, ``end_hub``, and
        ``hub`` – using a shared regex pattern.  The resulting ``Zone``
        object is added to ``self.network`` and, when appropriate, set as
        the network's start or end zone.

        Expected line format::

            <hub_type>: <name> <x> <y> [key=value ...]

        Args:
            hub_type (str): One of ``"start_hub"``, ``"end_hub"``, or
                ``"hub"``.
            stripped_line (str): The full (already stripped) source line.
            line_num (int): 1-based line number used in error messages.

        Raises:
            ValueError: If ``self.network`` has not been initialised yet
                (i.e. the ``nb_drones:`` line has not been parsed).
            ValueError: If the coordinate values cannot be parsed as
                integers.
        """
        pattern = (
            rf"{hub_type}:\s+(\w+)\s+(-?\d+)\s+(-?\d+)\s*(?:\[([^\]]*)\])?"
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
                    msg = "Found an end_hub before defining nb_drones"
                    raise ValueError(msg)

                try:
                    end_hub = Zone(
                        name, val1, val2, zone_type, max_drones, color
                    )
                    self.network.add_zone(end_hub)
                    self.network.set_end(end_hub)
                    self.zones[name] = end_hub

                except ValueError:
                    msg = f"Line {line_num}: Coordinates must be integers"
                    raise ValueError(msg)

            elif hub_type == "hub":
                if self.network is None:
                    msg = "Found a hub before defining nb_drones"
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

    def parse(self) -> Network:
        """Parse the map file and return the fully constructed ``Network``.

        Reads the file line by line, skipping blank lines and comments
        (``#``), and dispatches each directive to the appropriate handler.
        The method is single-use per instance; calling it a second time
        raises a ``RuntimeError``.

        Returns:
            Network: The populated network with all zones, connections,
                start zone, and end zone set.

        Raises:
            RuntimeError: If ``parse()`` has already been called on this
                instance.
            ValueError: If the file is empty or does not begin with an
                ``nb_drones:`` directive.
            ValueError: If any line contains malformed data (bad zone types,
                unknown zone references in connections, etc.).
        """
        if self.network is not None:
            msg = "Network has already been parsed for this instance!"
            raise RuntimeError(msg)
        with open(self.path, "r") as file:
            for line_num, line in enumerate(file, 1):
                stripped = line.strip()
                if not stripped:
                    continue
                # Some map files prefix start_hub with '#' as a visual marker.
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

                if stripped.startswith("start_hub:"):
                    self._parse_hub("start_hub", stripped, line_num)
                    continue
                elif stripped.startswith("end_hub:"):
                    self._parse_hub("end_hub", stripped, line_num)
                    continue
                elif stripped.startswith("hub:"):
                    self._parse_hub("hub", stripped, line_num)
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
                            print(f"DEBUG: Looking for {val1}, {val2}")
                            zones_list = list(self.zones.keys())
                            print(f"DEBUG: Available zones: {zones_list}")
                            msg = (
                                f"Line {line_num}: Connection refers to "
                                "unknown zones"
                            )
                            raise ValueError(msg)
                    continue

        if self.network is None:
            raise ValueError("The file is empty or missing 'nb_drones:'")
        return self.network


if __name__ == "__main__":
    my_parser = MapParser(path_to_the_file)
    built_network = my_parser.parse()

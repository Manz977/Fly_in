from typing import Optional
from models import Network


path_to_the_file = "../maps/simple_map.txt"



def parse_map(path: str) -> Network:
    network: Optional[Network] = None

    with open(path, "r") as file:
       for line_num, line in enumerate(file, 1):
           stripped = line.strip()

           if not stripped or stripped.startswith("#"):
               continue

           if network is None:
               if not stripped.startswith("nb_drones:"):
                   raise ValueError(f"Line {line_num}: First data line must be 'nb_drones:")
               try:
                    parts = stripped.split(":")
                    if len(parts) < 2:
                        raise ValueError("Missing value after 'nb_drones:'")
                    num_dr = int(parts[1].strip())
                    network = Network(num_dr)
               except ValueError as e:
                   raise ValueError(f"Line {line_num}: Invalid drone count - {e}")
               continue
            ##if stripped.startswith("start_hub:"):
            ##    label, content = stripped.split(":", 1)

            #    #parts = content.strip().split()

            #    if len(parts) < 3:
            #        raise ValueError(f"Line {line_num}")











    if network is None:
        raise ValueError("The file is empty or missing 'nb_drones:'")
    return network

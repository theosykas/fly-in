from typing import Dict, List


class MetadataConnection:
    def __init__(self, capacity_link: int = 1) -> None:
        self.max_link = capacity_link


class MetadataHub:
    def __init__(self, color: str = "grey", capacity: int = 1):
        self.color = color
        self.type_zone: str = "normal"
        self.max_drones: int = capacity
        self.is_blocked_zone: bool = False


class Connection:
    def __init__(self, z_1: str, z_2: str) -> None:
        self.z_1 = z_1
        self.z_2 = z_2


class Zone:
    def __init__(self, name: str, x: int, y: int) -> None:
        self.name = name
        self.x: int = x
        self.y: int = y


class Drone:
    def __init__(self, ids: str) -> None:
        self.ids: str = ids
        self.current_zone: str = ""
        self.next_zone: str = ""
        self.is_fly: bool = False


class Reader:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.drones: List[Drone] = []
        self.nb_drones: int = 0
        self.zone: Dict[str, Zone] = {}
        self.connection: List[Connection] = []

    def parse_map(self) -> None:
        valid_hub: tuple = (("hub:", "start_hub:", "end_hub:"))
        try:
            with open(self.file_path, 'r') as file:
                for line in file:
                    line: str = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("nb_drones:"):
                        split_arg = line.split(":")
                        self.nb_drones = int(split_arg[1].strip())
                        if self.nb_drones < 0:
                            ERROR_MSG = "[Error] you must have "
                            ERROR_MSG += "at least one drone"
                            raise ValueError(ERROR_MSG)
                        for id in range(self.nb_drones):
                            drones_ids = f"D{id + 1}"
                            self.drones.append(Drone(drones_ids))
                    elif line.startswith(valid_hub):
                        name_hub, pos = line.split(":", 1)
                        clean_hub = pos.split('[')[0].strip().split()  # stop to metadata
                        if '-' in name_hub:
                            ERROR_MSG = "you cant have dash in zone"
                            raise ValueError(ERROR_MSG)
                        if len(clean_hub) < 3:
                            ERROR_MSG = "[Error] missing positional argument"
                            ERROR_MSG += "<x> or <y>"
                            raise ValueError(ERROR_MSG)
                        hub_type = clean_hub[0]
                        try:
                            x_pos = int(clean_hub[1])
                            y_pos = int(clean_hub[2])
                        except ValueError:
                            raise ValueError("the hub must be int <x> <y>")
                        create_zone = Zone(name=hub_type, x=x_pos, y=y_pos)
                        if name_hub == "start_hub":
                            self.start_zone = hub_type
                        elif name_hub == "end_hub":
                            self.end_zone = hub_type
                        self.zone[hub_type] = create_zone
                    elif line.startswith("connection:"):
                        _, connection_parts = line.split(":", 1)
                        clean_connection = connection_parts.split('[')[0].strip()
                        zone = clean_connection.split('-')
                        if len(zone) != 2:
                            ERROR_MSG = "[Error] you need two"
                            ERROR_MSG = " zone to connection"
                            raise ValueError(ERROR_MSG)
                        zone_1 = zone[0]
                        zone_2 = zone[1]
                        if '-' not in clean_connection:
                            ERROR_MSG = "[Error] you must have dash"
                            ERROR_MSG += "in connection"
                            raise ValueError(ERROR_MSG)
                        if zone_1 in self.zone and zone_2 in self.zone:
                            self.connection.append(Connection(zone_1, zone_2))
                        bidirectional_create = Connection(
                            z_1=zone_1,
                            z_2=zone_2)
                        if bidirectional_create not in self.connection:
                            self.connection.append(bidirectional_create)
        except FileNotFoundError:
            print('Error file is not found')
        except Exception as e:
            print(f"parsing {e}")
            exit(1)


# bidirectionnel, bidirectionnelle
# Qui peut assurer dans les deux sens la liaison entre deux éléments.

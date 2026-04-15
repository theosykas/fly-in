from typing import Dict, List, Optional
from colorama import Fore, Style


class MetadataConnection:
    def __init__(self, capacity_link: int = 1) -> None:
        self.max_link: int = capacity_link


class MetadataHub:
    def __init__(self, color: str = "grey", capacity: int = 1):
        self.is_blocked: bool = False
        self.max_drones: int = capacity
        self.type_zone: str = "normal"
        self.color = color


class Connection:
    def __init__(self, z_1: str, z_2: str) -> None:
        self.metadata: Optional[MetadataConnection] = None
        self.drones_transit: List[str] = []
        self.z_1 = z_1
        self.z_2 = z_2


class Zone:
    def __init__(self, name: str, x: int, y: int) -> None:
        self.metadata: Optional[MetadataHub] = None
        self.name = name
        self.x: int = x
        self.y: int = y


class Drone:
    def __init__(self, ids: str) -> None:
        self.current_zone: str = ""
        self.path: List[str] = []
        self.is_fly: bool = False
        self.next_zone: str = ""
        self.wait_turn: int = -1
        self.ids: str = ids


class Reader:
    def __init__(self, file_path: str) -> None:
        self.adj_neigboor: Dict[str, List[str]] = {}
        self.connection: Dict[str, Connection] = {}
        self.connection_type: Dict[str, str] = {}
        self.zone_type: Dict[str, str] = {}
        self.zone: Dict[str, Zone] = {}
        self.drones: List[Drone] = []
        self.file_path = file_path
        self.nb_drones: int = 0

    def max_link_cap(self, link_name: str) -> int:
        default_cap = 1
        link_capacity = self.connection.get(link_name)
        if link_capacity and link_capacity.metadata:
            return int(link_capacity.metadata.max_link)
        return default_cap

    def max_drone_cap(self, zone_name: str) -> int:
        default_cap = 1
        zone_cap = self.zone.get(zone_name)
        if zone_cap and zone_cap.metadata:
            return int(zone_cap.metadata.max_drones)
        return default_cap

    def get_neighboor(self, zone_name: str) -> List[str]:
        return self.adj_neigboor.get(zone_name, [])

    def get_zone_type(self, zone_name: str) -> str:
        return self.zone_type.get(zone_name, "normal")

    def get_connection(self, z1: str, z2: str) -> Optional[Connection]:
        if f"{z1}-{z2}" in self.connection:
            return self.connection[f"{z1}-{z2}"]
        if f"{z2}-{z1}" in self.connection:
            return self.connection[f"{z2}-{z1}"]
        return None

    def valide_pos(self) -> None:
        ERROR_MSG = ""
        if not hasattr(self, "start_zone"):
            raise ValueError("missing <start_hub:>")
        if not hasattr(self, "end_zone"):
            raise ValueError("missing <end_hub:>")
        for key, co in self.connection.items():
            if co.z_1 not in self.zone:
                ERROR_MSG = f"unknown zone '{co.z_1}' in connection"
                ERROR_MSG += f"{key}"
                raise ValueError(ERROR_MSG)
            if co.z_2 not in self.zone:
                ERROR_MSG = f"unknown zone '{co.z_2}' in connection"
                ERROR_MSG += f"{key}"
                raise ValueError(ERROR_MSG)

    def parse_drone(self, line: str) -> None:
        split_arg = line.split(":")
        self.nb_drones = int(split_arg[1].strip())
        if self.nb_drones <= 0:
            ERROR_MSG = "you must have "
            ERROR_MSG += "at least one drone"
            raise ValueError(ERROR_MSG)
        for id in range(self.nb_drones):
            drones_ids = f"D{id + 1}"
            self.drones.append(Drone(drones_ids))

    def parse_hub(self, line: str) -> None:
        name_hub, content = line.split(":", 1)
        if '[' in content:
            parts = content.split('[', 1)
            data_hub = parts[0].strip()
            metadata_raw = parts[1]
            if metadata_raw.count(']') != 1:
                raise ValueError('too many brackets')
            if metadata_raw.count('[') != 0:
                ERROR_MSG = 'opening brace'
                ERROR_MSG += "into metadata"
                raise ValueError(ERROR_MSG)
            metadata_hub = metadata_raw.rstrip(']').strip()
        else:
            data_hub = content.strip()
            metadata_hub = ""
        hub_parts = data_hub.split()
        if len(hub_parts) != 3:
            ERROR_MSG = "Invalid hub format"
            ERROR_MSG += " <hub> <x> <y>"
            raise ValueError(ERROR_MSG)
        hub_name = hub_parts[0]
        if '-' in hub_name:
            ERROR_MSG = "invalid hub_name"
            ERROR_MSG += f" {hub_name}"
            raise ValueError(ERROR_MSG)
        try:
            x_pos = int(hub_parts[1])
            y_pos = int(hub_parts[2])
        except ValueError:
            raise ValueError("Coordinate must be int")

        curr_metadata = MetadataHub()  # recover meta
        if metadata_hub:
            metadata_parts = metadata_hub.split()
            double_meta = set()
            valid_zone = {'blocked',
                          'normal',
                          'restricted',
                          'priority'}
            for p in metadata_parts:
                if '=' not in p:
                    ERROR_MSG = "missing '=' into "
                    ERROR_MSG += "metadata [meta=data]"
                    raise ValueError(ERROR_MSG)

                key, value = p.split('=', 1)

                if key in double_meta:
                    raise ValueError("duplicate metadata")
                double_meta.add(key)

                if '=' in p:
                    allowed_keys = {'color',
                                    'zone',
                                    'max_drones'}
                    if key not in allowed_keys:
                        ERROR_MSG = "extra_keys"
                        ERROR_MSG += f" {key}"
                        raise ValueError(ERROR_MSG)
                    if not value:
                        raise ValueError(f' empy value for key {key}')
                    if key == 'color':
                        curr_metadata.color = value
                    elif key == 'zone':
                        if value not in valid_zone:
                            raise ValueError(
                                        'invalid zone input')
                        curr_metadata.type_zone = value
                        if value == 'blocked':
                            curr_metadata.is_blocked = True
                    elif key == 'max_drones':
                        try:
                            val = int(value)
                        except ValueError:
                            ERROR_MSG = "max_drones"
                            ERROR_MSG += " must be integer"
                            raise ValueError(ERROR_MSG)
                        if val <= 0:
                            ERROR_MSG = "max_drones "
                            ERROR_MSG += "must be positive int"
                            raise ValueError(ERROR_MSG)
                        curr_metadata.max_drones = val
        create_zone = Zone(name=hub_name, x=x_pos, y=y_pos)
        create_zone.metadata = curr_metadata
        if name_hub == "start_hub":
            self.start_zone = hub_name
        elif name_hub == "end_hub":
            self.end_zone = hub_name
        self.zone[hub_name] = create_zone
        self.zone_type[hub_name] = curr_metadata.type_zone

    def parse_connection(self, line: str) -> None:
        _, connection_parts = line.split(":", 1)
        if '[' in connection_parts:
            parts = connection_parts.split('[', 1)
            data_connections = parts[0].strip()
            metadata_raw = parts[1]
            if metadata_raw.count(']') != 1:
                raise ValueError('too many brackets')
            if metadata_raw.count('[') != 0:
                ERROR_MSG = 'opening brace'
                ERROR_MSG += " opening brace"
                raise ValueError(ERROR_MSG)
            metadata = metadata_raw.rstrip(']').strip()
        else:
            data_connections = connection_parts.strip()
            metadata = ""
        if '-' not in data_connections:
            ERROR_MSG = "you must have dash"
            ERROR_MSG += "in connection"
            raise ValueError(ERROR_MSG)
        zone = data_connections.split('-')
        if len(zone) != 2:
            ERROR_MSG = "you need two"
            ERROR_MSG += " zone to connection"
            raise ValueError(ERROR_MSG)
        zone_1 = zone[0].strip()
        zone_2 = zone[1].strip()
        if zone_1 not in self.adj_neigboor:
            self.adj_neigboor[zone_1] = []
        if zone_2 not in self.adj_neigboor:
            self.adj_neigboor[zone_2] = []
        if zone_1 not in self.adj_neigboor[zone_2]:
            self.adj_neigboor[zone_2].append(zone_1)
        if zone_2 not in self.adj_neigboor[zone_1]:
            self.adj_neigboor[zone_1].append(zone_2)

        curr_meta_conn = MetadataConnection()
        if metadata:
            meta_parts = metadata.split()
            double_meta = set()
            for p in meta_parts:

                if '=' not in p:
                    ERROR_MSG = "missing '=' into"
                    ERROR_MSG += " metadata [meta=data]"
                    raise ValueError(ERROR_MSG)

                if '=' in p:
                    key, value = p.split('=', 1)

                    if key in double_meta:
                        ERROR_MSG = "duplicate"
                        ERROR_MSG += " metadata"
                        raise ValueError(ERROR_MSG)
                    double_meta.add(key)

                    allowed_keys = {'max_link_capacity'}
                    if key not in allowed_keys:
                        ERROR_MSG = "extra_keys"
                        ERROR_MSG += f" {key}"
                        raise ValueError(ERROR_MSG)

                    if key == 'max_link_capacity':
                        try:
                            val = int(value)
                        except ValueError:
                            ERROR_MSG = "max_link"
                            ERROR_MSG += "must be intger"
                            raise ValueError(ERROR_MSG)
                        if val <= 0:
                            ERROR_MSG = "max_link must"
                            ERROR_MSG += " be positive integer"
                            raise ValueError(ERROR_MSG)
                        curr_meta_conn.max_link = val

        if zone_1 in self.zone and zone_2 in self.zone:
            key_1 = f"{zone_1}-{zone_2}"
            key_2 = f"{zone_2}-{zone_1}"

            if key_1 in self.connection or key_2 in self.connection:
                raise ValueError(f"duplicate connection: {key_1}")
            bidirectional_create = Connection(
                z_1=zone_1,
                z_2=zone_2)
            bidirectional_create.metadata = curr_meta_conn
            key = f"{zone_1}-{zone_2}"
            if key not in self.connection:
                self.connection[key_1] = bidirectional_create

    def parse_map(self) -> None:
        valid_hub: tuple[str, str, str] = ("hub",
                                           "start_hub",
                                           "end_hub")
        valid_first_line: bool = False

        try:
            with open(self.file_path, 'r') as file:
                for line_nb, line in enumerate(file, start=1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    if not valid_first_line:
                        valid_first_line = True  # err
                        if not line.startswith("nb_drones:"):
                            ERROR_MSG = "you map must be start"
                            ERROR_MSG += " with <nb_drones>"
                            raise ValueError(ERROR_MSG)

                    if line.startswith("nb_drones:"):
                        self.parse_drone(line)
                    elif line.startswith(valid_hub):
                        self.parse_hub(line)
                    elif line.startswith("connection:"):
                        self.parse_connection(line)
                    else:
                        format = line.split(':')[0]
                        raise ValueError(f'unknow format "{format}" directive')
            self.valide_pos()
        except FileNotFoundError:
            print('Error file is not found')
        except Exception as e:
            print(f"{Fore.RED} [Error] [Line: {line_nb}]{Style.RESET_ALL} {e}")
            exit(0)

from typing import Dict, List, Optional


class MetadataConnection:
    def __init__(self, capacity_link: int = 1) -> None:
        self.max_link = capacity_link


class MetadataHub:
    def __init__(self, color: str = "grey", capacity: int = 1):
        self.is_blocked_zone: bool = False
        self.max_drones: int = capacity
        self.type_zone: str = "normal"
        self.color = color


class Connection:
    def __init__(self, z_1: str, z_2: str) -> None:
        self.z_1 = z_1
        self.z_2 = z_2
        self.metadata = None
        self.drones_transit: List[str] = []


class Zone:
    def __init__(self, name: str, x: int, y: int) -> None:
        self.name = name
        self.x: int = x
        self.y: int = y
        self.metadata: Optional[MetadataHub] = None


class Drone:
    def __init__(self, ids: str) -> None:
        self.current_zone: str = ""
        self.is_fly: bool = False
        self.next_zone: str = ""
        self.ids: str = ids
        self.wait_turn: int = -1
        self.path: List[str] = []


class Reader:
    def __init__(self, file_path: str):
        self.connection: List[Connection] = []
        self.zone: Dict[str, Zone] = {}
        self.drones: List[Drone] = []
        self.file_path = file_path
        self.nb_drones: int = 0
        self.zone_type: Dict[str, str] = {}
        self.adj_neigboor: Dict[str, List[str]] = {}
        self.connection_type: Dict[str, str] = {}

    def max_link_cap(self):
        pass

    def max_drone_cap(self, zone_name: str) -> int:
        default_cap = 50
        zone_cap = self.zone.get(zone_name)
        if zone_cap and zone_cap.metadata:
            return zone_cap.metadata.max_drones
        return default_cap

    def get_neighboor(self, zone_name: str) -> str:
        return self.adj_neigboor.get(zone_name, [])

    def get_zone_type(self, zone_name: str) -> str:
        return self.zone_type.get(zone_name, "normal")

    def get_connection(self, z1: str, z2: str) -> Optional[Connection]:
        for co in self.connection:
            if (co.z_1 == z1 and co.z_2 == z2) or (co.z_1 == z2 and co.z_2 == z1):
                return co
        return None

    def parse_map(self) -> None:
        valid_hub: tuple = ("hub:", "start_hub:", "end_hub:")
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
                    # hub_parts
                    elif line.startswith(valid_hub):
                        name_hub, content = line.split(":", 1)
                        if '[' in content:
                            parts = content.split('[', 1)
                            data_hub = parts[0].strip()
                            metadata_hub = parts[1].rstrip(']').strip()
                        else:
                            data_hub = content.strip()
                            metadata_hub = ""
                        if '-' in name_hub:
                            ERROR_MSG = "you cant have dash in zone"
                            raise ValueError(ERROR_MSG)
                        if len(data_hub) < 3:
                            ERROR_MSG = "[Error] missing positional argument"
                            ERROR_MSG += "<x> or <y>"
                            raise ValueError(ERROR_MSG)
                        hub_parts = data_hub.split()
                        hub_name = hub_parts[0]
                        try:
                            x_pos = int(hub_parts[1])
                            y_pos = int(hub_parts[2])
                        except ValueError:
                            raise ValueError("the hub must be int <x> <y>")
                        curr_metadata = MetadataHub()  # recover meta
                        if metadata_hub:
                            metadata_parts = metadata_hub.split()
                            for p in metadata_parts:
                                valid_zone = {'blocked',
                                              'normal',
                                              'restricted',
                                              'priority'}
                                key, value = p.split('=', 1)
                                if '=' in p:
                                    if key == 'color':
                                        curr_metadata.color = value
                                    elif key == 'zone':
                                        if value not in valid_zone:
                                            raise ValueError(
                                                'Error invalid zone input')
                                        curr_metadata.type_zone = value  # zone courrante
                                        if value == 'blocked':
                                            curr_metadata.is_blocked_zone = True  # zone act blocked
                                    elif key == 'max_drones':
                                        curr_metadata.max_drones = int(value)
                        create_zone = Zone(name=hub_name, x=x_pos, y=y_pos)
                        create_zone.metadata = curr_metadata  # add attribue metadata
                        if name_hub == "start_hub":
                            self.start_zone = hub_name
                        elif name_hub == "end_hub":
                            self.end_zone = hub_name
                        self.zone[hub_name] = create_zone
                        self.zone_type[hub_name] = curr_metadata.type_zone
                    # connection parts
                    elif line.startswith("connection:"):
                        _, connection_parts = line.split(":", 1)
                        if '[' in connection_parts:
                            parts = connection_parts.split('[', 1)
                            data_connections = parts[0].strip()
                            metadata = parts[1].rstrip(']').strip()  # interieur crochet []
                        else:
                            data_connections = connection_parts.strip()
                            metadata = ""
                        if '-' not in data_connections:
                            ERROR_MSG = "[Error] you must have dash"
                            ERROR_MSG += "in connection"
                            raise ValueError(ERROR_MSG)
                        zone = data_connections.split('-')
                        if len(zone) != 2:
                            ERROR_MSG = "[Error] you need two"
                            ERROR_MSG += " zone to connection"
                            raise ValueError(ERROR_MSG)
                        zone_1 = zone[0].strip()
                        zone_2 = zone[1].strip()
                        if zone_1 not in self.adj_neigboor:
                            self.adj_neigboor[zone_1] = []
                        if zone_2 not in self.adj_neigboor:
                            self.adj_neigboor[zone_2] = []
                        # bidirectional
                        if zone_1 not in self.adj_neigboor[zone_2]:  # check si zone_1 est dans la zone_2
                            self.adj_neigboor[zone_2].append(zone_1)
                        if zone_2 not in self.adj_neigboor[zone_1]:
                            self.adj_neigboor[zone_1].append(zone_2)
                        curr_metadata = MetadataConnection()
                        if metadata:
                            meta_parts = metadata.split()
                            for p in meta_parts:
                                if '=' in p:
                                    key, value = p.split('=', 1)
                                    if key == 'max_link_capacity':
                                        curr_metadata.max_link = value
                        if zone_1 in self.zone and zone_2 in self.zone:
                            bidirectional_create = Connection(
                                z_1=zone_1,
                                z_2=zone_2)
                            bidirectional_create.metadata = curr_metadata
                            if bidirectional_create not in self.connection:
                                self.connection.append(bidirectional_create)
        except FileNotFoundError:
            print('Error file is not found')
        except Exception as e:
            print(f"parsing {e}")
            exit(1)


# bidirectionnel, bidirectionnelle
# Qui peut assurer dans les deux sens la liaison entre deux éléments.

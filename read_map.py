from typing import Dict, List, Optional
from colorama import Fore, Style


class MetadataConnection:
    """Manages metadata for connections between zones.

         Attributes:
             max_link (int): Maximum number of drones allowed to traverse
                 the connection simultaneously.
         """
    def __init__(self, capacity_link: int = 1) -> None:
        """Initializes connection metadata.

             Args:
                 capacity_link (int): The link capacity. Defaults to 1.
         """
        self.max_link: int = capacity_link


class MetadataHub:
    """Manages metadata for hubs (zones).

         Attributes:
             is_blocked (bool): Whether the hub is inaccessible.
             max_drones (int): Maximum number of drones the hub can hold.
             type_zone (str): The classification of the zone
             (e.g., 'normal', 'priority').
             color (str): Visual color identifier for the hub.
         """
    def __init__(self, color: str = "grey", capacity: int = 1):
        """Initializes hub metadata.

             Args:
                 color (str): Color of the hub. Defaults to "grey".
                 capacity (int): Drone capacity. Defaults to 1.
         """
        self.is_blocked: bool = False
        self.max_drones: int = capacity
        self.type_zone: str = "normal"
        self.color = color


class Connection:
    """Represents a bidirectional link between two zones.

         Attributes:
             metadata (Optional[MetadataConnection]): Capacity and link rules.
             drones_transit (List[str]): List of drone IDs currently on this
             link.
             z_1 (str): Name of the first connected zone.
             z_2 (str): Name of the second connected zone.
     """
    def __init__(self, z_1: str, z_2: str) -> None:
        """Initializes a connection.

             Args:
                 z_1 (str): Name of the first zone.
                 z_2 (str): Name of the second zone.
             """
        self.metadata: Optional[MetadataConnection] = None
        self.drones_transit: List[str] = []
        self.z_1 = z_1
        self.z_2 = z_2


class Zone:
    """Represents a physical location (hub) on the map.

         Attributes:
             metadata (Optional[MetadataHub]): Hub specific rules and
             properties.
             name (str): Unique identifier for the zone.
             x (int): Horizontal coordinate.
             y (int): Vertical coordinate.
     """
    def __init__(self, name: str, x: int, y: int) -> None:
        """Initializes a zone.

             Args:
                 name (str): Zone identifier.
                 x (int): X coordinate.
                 y (int): Y coordinate.
         """
        self.metadata: Optional[MetadataHub] = None
        self.name = name
        self.x: int = x
        self.y: int = y


class Drone:
    """Represents a drone in the simulation.

         Attributes:
             current_zone (str): Current location of the drone.
            path (List[str]): List of zones to visit.
            is_fly (bool): True if the drone is currently moving.
            next_zone (str): Target zone for the current move.
            wait_turn (int): Remaining turns to wait at a restricted zone.
            ids (str): Unique drone identifier.
     """
    def __init__(self, ids: str) -> None:
        """Initializes a drone.
            Args:
                ids (str): Drone ID.
         """
        self.current_zone: str = ""
        self.path: List[str] = []
        self.is_fly: bool = False
        self.next_zone: str = ""
        self.wait_turn: int = -1
        self.ids: str = ids


class Reader:
    """Parses map files and stores simulation state.

        Attributes:
            adj_neigboor (Dict[str, List[str]]): Adjacency list for the graph.
            connection (Dict[str, Connection]): Dictionary of all map links.
            connection_type (Dict[str, str]): Mapping of connection IDs to
            types.
            zone_type (Dict[str, str]): Mapping of zone names to types.
            zone (Dict[str, Zone]): Dictionary of all map zones.
            drones (List[Drone]): List of active drones.
            file_path (str): Source path of the map file.
            nb_drones (int): Total number of drones defined.
        """
    def __init__(self, file_path: str) -> None:
        """Initializes the reader.

            Args:
                file_path (str): Path to the map file.
         """
        self.adj_neigboor: Dict[str, List[str]] = {}
        self.connection: Dict[str, Connection] = {}
        self.connection_type: Dict[str, str] = {}
        self.zone_type: Dict[str, str] = {}
        self.zone: Dict[str, Zone] = {}
        self.drones: List[Drone] = []
        self.file_path = file_path
        self.nb_drones: int = 0

    def max_link_cap(self, link_name: str) -> int:
        """Gets the maximum capacity of a specific link.

            Args:
                link_name (str): The connection identifier (e.g., 'A-B').

            Returns:
                int: The capacity limit.
         """
        default_cap = 1
        link_capacity = self.connection.get(link_name)
        if link_capacity and link_capacity.metadata:
            return int(link_capacity.metadata.max_link)
        return default_cap

    def max_drone_cap(self, zone_name: str) -> int:
        """Gets the maximum drone capacity of a zone.

            Args:
                zone_name (str): Name of the hub.

            Returns:
                int: Maximum drones allowed.
            """
        default_cap = 1
        zone_cap = self.zone.get(zone_name)
        if zone_cap and zone_cap.metadata:
            return int(zone_cap.metadata.max_drones)
        return default_cap

    def get_neighboor(self, zone_name: str) -> List[str]:
        """Returns the list of neighboring zones.

            Args:
                zone_name (str): The source zone.

            Returns:
                List[str]: List of names of adjacent zones.
         """
        return self.adj_neigboor.get(zone_name, [])

    def get_zone_type(self, zone_name: str) -> str:
        """Gets the type of a specific zone.

            Args:
                zone_name (str): The hub name.

            Returns:
                str: Zone type (e.g., 'normal', 'priority').
         """
        return self.zone_type.get(zone_name, "normal")

    def get_connection(self, z1: str, z2: str) -> Optional[Connection]:
        """Retrieves a connection object between two zones.

            Args:
                z1 (str): First zone name.
                z2 (str): Second zone name.

            Returns:
                Optional[Connection]: The connection object if found.
        """
        if f"{z1}-{z2}" in self.connection:
            return self.connection[f"{z1}-{z2}"]
        if f"{z2}-{z1}" in self.connection:
            return self.connection[f"{z2}-{z1}"]
        return None

    def valide_pos(self) -> None:
        """Validates that start/end hubs exist and connections are valid.

            Raises:
                ValueError: If critical hubs are missing or zones are unknown.
        """
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
        """Parses the drone count line and initializes drone objects.

            Args:
                line (str): Raw string from map file.

            Raises:
                ValueError: If drone count is zero or negative.
        """
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
        """Parses a hub definition line including its metadata.

            Args:
                line (str): Raw string from map file.

            Raises:
                ValueError: For incorrect format, duplicate metadata or
                invalid values.
         """
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
        """Parses a connection definition line including its metadata.

                    Args:
                line (str): Raw string from map file.

            Raises:
                ValueError: For incorrect format or invalid metadata values.
            """
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
        """Main entry point to read and parse the entire map file.

            Iterates through the file and delegates to specific parsing
            functions
            based on line content. Finally validates the map structure.
        """
        valid_hub: tuple[str, str, str] = ("hub",
                                           "start_hub",
                                           "end_hub")
        valid_first_line: bool = False
        delayed_connection = []
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
                        delayed_connection.append((line_nb, line))
                    else:
                        format = line.split(':')[0]
                        raise ValueError(f'unknow format "{format}" directive')
                for l_nb, l_content in delayed_connection:
                    line_nb = l_nb
                    self.parse_connection(l_content)
            self.valide_pos()
        except FileNotFoundError:
            print('Error file is not found')
        except Exception as e:
            print(f"{Fore.RED} [Error] [Line: {line_nb}]{Style.RESET_ALL} {e}")
            exit(0)

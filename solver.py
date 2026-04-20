from typing import List, Dict, Set, Optional
from heapq import heappop, heappush
from colorama import Fore, Style
from read_map import Reader


class Solver:
    """Handles pathfinding and drone movement simulation.

         Attributes:
             mem_connection (Dict[str, tuple[str, str]]): Stores temporary
                 connection data for drones in transit.
             wait_restricted (Dict[str, bool]): Tracks if a drone is currently
                 waiting in a restricted zone.
             path (Dict[str, List[str]]): Maps drone IDs to their assigned
             paths.
             occupacy (Dict[str, int]): Tracks current drone count in each
             zone.
             step (Dict[str, int]): Tracks the current path index for each
             drone.
             is_finished (Set[str]): Set of drone IDs that have reached the
             destination.
             reader (Reader): Reference to the map reader object.
     """
    def __init__(self, reader: Reader) -> None:
        """Initializes the solver with map data.

             Args:
                 reader (Reader): The parsed map data.
         """
        self.mem_connection: Dict[str, tuple[str, str]] = {}
        self.wait_restricted: Dict[str, bool] = {}
        self.path: Dict[str, List[str]] = {}
        self.occupacy: Dict[str, int] = {}
        self.step: Dict[str, int] = {}
        self.is_finished: Set[str] = set()
        self.reader = reader

    def find_k_path(self, nb_path: int) -> List[List[str]]:
        """Finds multiple paths by applying penalties to used zones.

             Args:
                 nb_path (int): Number of paths to attempt to find.

             Returns:
                 List[List[str]]: A list of paths, where each path is a list
                 of zone names.
         """
        penality_zone: Dict[str, int] = {}
        penality_num: int = 2
        paths: List[List[str]] = []
        for _ in range(nb_path):
            path = self.dijkstra(penality=penality_zone, start_idx=None)
            if not path:
                break
            paths.append(path)

            for inter_zone in path[1:-1]:
                penality_zone[inter_zone] = penality_zone.get(
                    inter_zone, 0) + penality_num
        return paths

    def dijkstra(self, penality: Dict[str, int],
                 start_idx: Optional[str] = None) -> List[str]:
        """Implements Dijkstra's algorithm to find the shortest path.

             Args:
                 penality (Dict[str, int]): Penalties applied to zone weights.
                 start_idx (Optional[str]): Starting zone name. Defaults to
                 start_zone.

             Returns:
                 List[str]: The shortest path as a list of zone names, or
                 empty if no path.
             """
        if start_idx:
            start_hub = start_idx
        else:
            start_hub = self.reader.start_zone
        end_hub = self.reader.end_zone
        priority_queue: List[tuple[int, str, List[str]]] = [(0,
                                                             start_hub,
                                                             [start_hub])]
        visited: Set[str] = set()
        while priority_queue:
            current_cost, current_node, find_path = heappop(
                priority_queue
            )
            if current_node in visited:
                continue
            if current_node == end_hub:
                return find_path
            visited.add(current_node)
            for neighboor in self.reader.get_neighboor(current_node):
                if self.reader.get_zone_type(neighboor) == "blocked":
                    continue
                cost_zone = 10
                if neighboor not in visited:
                    zone_type = self.reader.get_zone_type(neighboor)
                    if zone_type == "restricted":
                        cost_zone = 20
                    elif zone_type == "priority":
                        cost_zone = 9
                    cost_zone += penality.get(neighboor, 0)
                    heappush(
                        priority_queue,
                        (current_cost + cost_zone,
                         neighboor,
                         find_path + [neighboor]),
                    )
        return []

    def init_drone(self) -> None:
        """Initializes drones by assigning paths and setting starting
        positions.

            Finds available paths and distributes drones across them.
         """
        try:
            paths = self.find_k_path(nb_path=2)
            if not paths:
                print("Error - path not find")
                return
            start = self.reader.start_zone
            self.occupacy = {start: len(self.reader.drones)}
            num_paths = len(paths)
            for i, drone in enumerate(self.reader.drones):
                assign_path = paths[i % num_paths]
                self.path[drone.ids] = assign_path
                self.step[drone.ids] = 0
                drone.current_zone = start
                self.wait_restricted[drone.ids] = False
                drone.is_fly = False
        except Exception:
            print(f'{Fore.RED} Error initialize drones')
        return None

    def turn(self) -> tuple[bool, str]:
        """Executes one simulation turn for all drones.

            Manages drone movement logic, capacity constraints, and restricted
            zones.

            Returns:
                tuple[bool, str]: A tuple containing:
                    - bool: True if at least one drone moved or is still
                    active.
                    - str: A formatted string representing movements in this
                    turn.
         """
        turn_output: List[str] = []
        moving = False
        for drone in self.reader.drones:
            if drone.ids in self.is_finished:
                continue

            if self.step[drone.ids] < 0:
                self.step[drone.ids] += 1
                moving = True
                continue

            path = self.path.get(drone.ids, [])
            current_pos = self.step[drone.ids]
            next_step = current_pos + 1

            if next_step >= len(path):
                self.is_finished.add(drone.ids)
                self.occupacy[path[current_pos]] -= 1
                continue

            if next_step < len(path):
                next_zone = path[next_step]
                current_zone = path[current_pos]
                connection = self.reader.get_connection(current_zone,
                                                        next_zone)
                max_drones = self.reader.max_drone_cap(next_zone)
                current_occupacy = self.occupacy.get(next_zone, 0)

                max_link_cap = 1
                transit = 0
                if connection:
                    if connection.metadata:
                        max_link_cap = int(connection.metadata.max_link)
                    transit = len(connection.drones_transit)

                if self.wait_restricted.get(drone.ids, False):
                    self.wait_restricted[drone.ids] = False
                    z1, z2 = self.mem_connection.pop(drone.ids)
                    connection = self.reader.get_connection(z1, z2)
                    if connection:
                        connection.drones_transit.remove(drone.ids)
                    self.step[drone.ids] = next_step
                    drone.current_zone = next_zone
                    turn_output.append(f"{Fore.GREEN + drone.ids}"
                                       f"{Style.RESET_ALL}-{next_zone}")
                    moving = True
                    continue

                if current_occupacy < max_drones and transit < max_link_cap:
                    zone_cost = self.reader.get_zone_type(next_zone)
                    if zone_cost == "restricted":
                        if not self.wait_restricted.get(drone.ids, False):
                            self.wait_restricted[drone.ids] = True
                            self.occupacy[current_zone] -= 1
                            self.occupacy[next_zone] = current_occupacy + 1
                            connection = self.reader.get_connection(
                                current_zone, next_zone
                            )
                            if connection:
                                connection.drones_transit.append(drone.ids)
                                self.mem_connection[drone.ids] = (
                                    current_zone,
                                    next_zone,
                                )
                                conn_name = f"{connection.z_1}-"
                                conn_name += f"{connection.z_2}"
                                turn_output.append(f"{Fore.GREEN + drone.ids}"
                                                   f"{Style.RESET_ALL}-"
                                                   f"{conn_name}")
                            moving = True
                            continue
                    else:
                        self.occupacy[current_zone] -= 1
                        self.occupacy[next_zone] = current_occupacy + 1
                        self.step[drone.ids] = next_step
                        drone.current_zone = next_zone
                        turn_output.append(f"{Fore.GREEN + drone.ids}"
                                           f"{Style.RESET_ALL}-{next_zone}")
                        moving = True
                else:
                    moving = True
        return moving, " ".join(turn_output)

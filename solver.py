from heapq import heappop, heappush
from typing import List, Dict, Set
from read_map import Reader


class Solver:
    def __init__(self, reader: Reader) -> None:
        self.reader = reader
        self.path: Dict[str, List[str]] = {}  # drone id + path
        self.step: Dict[str, List[str]] = {}
        self.is_finished: Set[str] = set()

    def dijkstra(self) -> List[str]:  # a - c - d - f short path
        start_hub = self.reader.start_zone
        end_hub = self.reader.end_zone
        # 0 total_cost, start = current_node [start] = path parcourru
        priority_queue: List[tuple[int, str, List[str]]] = [(0, start_hub,
                                                             [start_hub])]
        visited: Set[str] = set()
        while priority_queue:  # non fini
            current_cost, current_node, find_path = heappop(
                priority_queue)  # heappop = min value path - couteux
            if current_node in visited:
                continue  # pass node visited
            if current_node == end_hub:
                print(find_path)
                return find_path
            visited.add(current_node)
            for neighboor in self.reader.get_neighboor(current_node):
                cost_zone = 1
                if neighboor not in visited:
                    zone_type = self.reader.get_zone_type(neighboor)
                    if zone_type == 'blocked':
                        continue
                    elif zone_type == 'restricted':
                        cost_zone = 2
                    update_cost = current_cost + cost_zone
                    heappush(priority_queue, (update_cost,
                                              neighboor,
                                              find_path + [neighboor]))
        return []  # no path

    def init_drone(self) -> None:
        path_find = self.dijkstra()
        if not path_find:
            print('Error - path not find')
            return
        for drone in self.reader.drones:
            self.path[drone.ids] = path_find
            self.step[drone.ids] = 0
            drone.current_zone = path_find[0]
            drone.is_fly = True
        return None

    def turn(self) -> bool:
        moving = False
        for drone in self.reader.drones:
            if drone.ids in self.is_finished:
                continue
            path = self.path.get(drone.ids, [])
            next_step = self.step[drone.ids] + 1
            if next_step < len(path):
                drone.current_zone = path[next_step]
                drone.next_zone = path[next_step + 1]
                drone.is_fly = True
                self.step[drone.ids] = next_step
                moving = True
            else:
                drone.is_fly = False
        return moving

# heappush: Ajoute un élément à la file d'attente avec sa priorité associée.

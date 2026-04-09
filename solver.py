from heapq import heappop, heappush
from typing import List, Dict, Set
from read_map import Reader


class Solver:
    def __init__(self, reader: Reader) -> None:
        self.reader = reader
        self.path: Dict[str, List[str]] = {}  # drone id + path
        self.step: Dict[str, List[str]] = {}
        self.is_finished: Set[str] = set()
        self.occupacy: Dict[str, int] = {}

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
        return []

    def init_drone(self) -> None:
        path_find = self.dijkstra()
        if not path_find:
            print('Error - path not find')
            return
        nb_drones = self.reader.start_zone
        self.occupacy = {nb_drones: len(self.reader.drones)}
        # start: 25
        for _, drone in enumerate(self.reader.drones):
            self.path[drone.ids] = path_find
            self.step[drone.ids] = 0
            drone.current_zone = nb_drones
            drone.is_fly = False
        return None

    def turn(self) -> bool:
        moving = False
        for drone in self.reader.drones:
            if drone.ids in self.is_finished:
                continue
            if self.step[drone.ids] < 0:  # step == -i (d0->d1->d2)
                self.step[drone.ids] += 1  # step (-) ++
                moving = True  # sim continue drone wait
                continue  # step == 0 on lance
            path = self.path.get(drone.ids, [])  # [start, gate_1 ....]
            current_pos = self.step[drone.ids]
            next_step = current_pos + 1  # prochaine case

            if next_step < len(path):  # step == 2 path[2]
                next_zone = path[next_step]
                current_zone = path[current_pos]
                max_drones = self.reader.max_drone_cap(next_zone)
                print(f"{drone.ids} capacity {max_drones} {next_zone}")
                current_occupacy = self.occupacy.get(next_zone, 0)
                if current_occupacy < max_drones:
                    # d0 ---->
                    self.occupacy[current_zone] -= 1
                    self.occupacy[next_zone] = current_occupacy + 1
                    self.step[drone.ids] = next_step
                    drone.current_zone = next_zone
                    moving = True
                else:
                    print(f"blocked {drone.ids} wait before {next_zone}")
                    drone.is_fly = False
                    moving = True
                zone_cost = self.reader.get_zone_type(next_zone)
                if zone_cost == "restricted":
                    wait_cost = 2
                else:
                    wait_cost = 1
                self.step[drone.ids] = next_step
                self.step[drone.ids] = next_step - (wait_cost - 1)
                print(f"cost zone {drone.ids} {wait_cost}")
            else:
                drone.is_fly = False
                self.is_finished.add(drone.ids)
                self.occupacy[path[current_pos]] -= 1  # libere la zone
                moving = True
        return moving

# heappush: Ajoute un élément à la file d'attente avec sa priorité associée.

# path [0 = start, 1 = hell1, 2 == maze]
# step == 2 path[2 == hell1]
# 2 = 1 == 3
# next_step < len(path)  3 < 5
# drone.current_zone = path[next_step] path[3]

# d step[] current_zone state
# --1
# d0 0    start         is_fly
# d1 -1   start         wait
# d2 -2   start         wait

# --2
# d0 1    gate_hell1    is_fly
# d1 0    start         is_fly
# d2 -1   start         wait

# --3
# d0 2   maze_1    is_fly
# d1 1   gate_1    is_fly
# d2 0   start     is_fly

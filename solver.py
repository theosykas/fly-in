from heapq import heappop, heappush
from typing import List, Dict, Set
from read_map import Reader


class Solver:
    def __init__(self, reader: Reader) -> None:
        self.reader = reader
        self.wait_restricted: Dict[str, bool] = {}
        self.step: Dict[str, int] = {}
        self.path: Dict[str, List[str]] = {}  # drone id + path
        self.mem_connection: Dict[str, tuple[str, str]] = {}
        self.occupacy: Dict[str, int] = {}
        self.is_finished: Set[str] = set()

    def dijkstra(self, extra_blocked: Set[str], start_idx: None) -> List[str]:  # a - c - d - f short path
        if start_idx:
            start_hub = start_idx
        else:
            start_hub = self.reader.start_zone
        end_hub = self.reader.end_zone
        # 0 total_cost, start = current_node [start] = path parcourru
        priority_queue: List[tuple[int, str, List[str]]] = [(0, start_hub, [start_hub])]
        visited: Set[str] = set()
        while priority_queue:  # non fini
            current_cost, current_node, find_path = heappop(
                priority_queue
            )  # heappop = min value path - couteux
            if current_node in visited:
                continue  # pass node visited
            if current_node == end_hub:
                return find_path
            visited.add(current_node)
            for neighboor in self.reader.get_neighboor(current_node):
                cost_zone = 1
                if neighboor not in visited:
                    if neighboor in extra_blocked:  # block zone deja utiliser
                        continue
                    zone_type = self.reader.get_zone_type(neighboor)
                    if zone_type == "blocked":
                        continue
                    elif zone_type == "restricted":
                        cost_zone = 2
                    update_cost = current_cost + cost_zone
                    heappush(
                        priority_queue,
                        (update_cost, neighboor, find_path + [neighboor]),
                    )
        return []

    def find_k_path(self, nb_path: int) -> List[int]:
        paths = []
        blocked_zone: set[str] = set()
        for _ in range(nb_path):
            path = self.dijkstra(extra_blocked=blocked_zone, start_idx=None)
            if not path:
                break
            paths.append(path)
            # forcew a trouver un autre chemin en zone blocked
            for inter_zone in path[1:-1]:  # 1 == start -1 ==goal
                blocked_zone.add(inter_zone)
        return paths

    def init_drone(self) -> None:
        try:
            paths = self.find_k_path(nb_path=2)  # 2 path
            if not paths:
                print("Error - path not find")
                return
            nb_drones = self.reader.start_zone
            self.occupacy = {nb_drones: len(self.reader.drones)}
            for i, drone in enumerate(self.reader.drones):
                path_pos = i % len(paths)
                self.path[drone.ids] = paths[path_pos]
                self.step[drone.ids] = -(i // len(paths))
                drone.current_zone = nb_drones
                drone.is_fly = False
                self.wait_restricted[drone.ids] = False
        except Exception:
            print('Error initialize drones')
            import traceback
            traceback.print_exc()
        return None

    def turn(self) -> bool:
        moving = False
        for drone in self.reader.drones:
            if drone.ids in self.is_finished:
                continue
            if self.step[drone.ids] < 0:  # step == -i (d0->d1->d2)
                self.step[drone.ids] += 1  # step (-) ++
                moving = True
                continue  # step == 0 on lance
            path = self.path.get(drone.ids, [])  # [start, gate_1 ....]
            current_pos = self.step[drone.ids]
            next_step = current_pos + 1  # prochaine case
            if next_step < len(path):  # step == 2 path[2]
                next_zone = path[next_step]
                current_zone = path[current_pos]
                max_drones = self.reader.max_drone_cap(next_zone)
                # print(f"{drone.ids} capacity {max_drones} {next_zone}")
                current_occupacy = self.occupacy.get(next_zone, 0)
                if self.wait_restricted.get(drone.ids, False):
                    self.wait_restricted[drone.ids] = False  # sort du link
                    z1, z2 = self.mem_connection.pop(drone.ids)
                    connection = self.reader.get_connection(z1, z2)
                    if connection:
                        connection.drones_transit.remove(drone.ids)
                    self.step[drone.ids] = next_step
                    drone.current_zone = next_zone
                    moving = True
                    continue
                if current_occupacy < max_drones:
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
                            moving = True
                            continue
                    else:
                        # d0 ----> normal zone
                        self.occupacy[current_zone] -= 1
                        self.occupacy[next_zone] = current_occupacy + 1
                        self.step[drone.ids] = next_step
                        drone.current_zone = next_zone
                        moving = True
                else:
                    satured_zone: Set[str] = set()
                    for zone, count_satured in self.occupacy.items():
                        if count_satured >= self.reader.max_drone_cap(zone) and count_satured > 0:
                            satured_zone.add(zone)
                    new_path = self.dijkstra(extra_blocked=satured_zone,
                                             start_idx=current_zone)
                    if new_path:
                        self.path[drone.ids] = new_path
                        if current_zone in new_path:
                            self.step[drone.ids] = new_path.index(current_zone)
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

from read_map import Reader
import pygame as py
import math


class InitWindow:
    def __init__(self, width: int, height: int, map_read: Reader) -> None:
        py.init()
        # self.mousse_position = (0, 0)
        self.height = height
        self.width = width
        self.map_read = map_read
        self.screen = py.display.set_mode((self.width, self.height))  # tuple set_mode
        self.clock_fps = py.time.Clock()
        py.display.set_caption("FLY-IN")
        self.zoom = 100
        self.BG_COLOR: str = "grey0"
        self.running_mode = True

    def draw_network(self) -> None:
        for co in self.map_read.connection:
            z1 = self.map_read.zone[co.z_1]
            z2 = self.map_read.zone[co.z_2]
            start_hub = (
                (z1.x * self.zoom) + (self.width // 4),
                (z1.y * self.zoom) + (self.height // 4),
            )
            end_hub = (
                (z2.x * self.zoom) + (self.width // 4),
                (z2.y * self.zoom) + (self.height // 4),
            )
            py.draw.line(self.screen, "white", start_hub, end_hub, 2)

    def draw_circle(self) -> None:
        mousse_p = py.mouse.get_pos()
        for _, zone in self.map_read.zone.items():
            radius = 10
            pos_x = (zone.x * self.zoom) + (self.width // 4)
            pos_y = (zone.y * self.zoom) + (self.height // 4)
            dist_x = mousse_p[0] - pos_x
            dist_y = mousse_p[1] - pos_y
            is_hooverd = math.hypot(dist_x, dist_y) < radius
            if is_hooverd:
                color = (85, 118, 171)
            else:
                color = (113, 135, 171)
            py.draw.circle(self.screen, color, (pos_x, pos_y), 12)

    def start_sim(self) -> None:
        while self.running_mode:
            for event in py.event.get():
                if event.type == py.QUIT:
                    self.running_mode = False
                elif event.type == py.MOUSEMOTION:
                    self.mousse_position = event.pos
            self.screen.fill(self.BG_COLOR)
            self.draw_network()
            self.draw_circle()
            py.display.flip()
            self.clock_fps.tick(60)
        py.quit()

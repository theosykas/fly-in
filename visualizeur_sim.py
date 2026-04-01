from read_map import Reader
from typing import List
import pygame as py
import math
import os


class FrameRainbow:
    def __init__(self, path: str, size: int, speed_frame: int = 5) -> None:
        self.path = path
        self.frames: List = []
        self.index_pos: int = 0
        self.count_frames: int = 0
        self.size = size
        self.speed = speed_frame
        self.frames = self.load_frames()

    def load_frames(self) -> list:
        frames = []
        for f in sorted(os.listdir(self.path)):
            if f.endswith(".jpg"):
                img = py.image.load(os.path.join(self.path, f)).convert_alpha()
                img = py.transform.scale(img, self.size)
                frames.append(img)
        return frames

    def update_frames(self) -> py.Surface:
        self.count_frames += 1
        if self.count_frames >= self.speed:
            self.count_frames = 0
            self.index_pos = (self.index_pos + 1) % len(self.frames)
        return self.frames[self.index_pos]


class Visualizeur:
    def __init__(self, width: int, height: int, map_read: Reader) -> None:
        py.init()
        self.height = height
        self.width = width
        self.map_read = map_read
        self.screen = py.display.set_mode(
            (self.width, self.height), py.RESIZABLE)
        self.clock_fps = py.time.Clock()
        py.display.set_caption("FLY-IN")
        self.zoom = 65
        self.BG_COLOR: str = "grey0"
        self.running_mode = True
        self.rainbow = FrameRainbow("frame_raindow", (40, 40), speed_frame=3)

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
        # texture = py.image.load("circle_rainbow.png")
        # rainbow_texture = py.transform.scale(texture, (20, 20))
        rainbow_frame = self.rainbow.update_frames()
        mousse_p = py.mouse.get_pos()
        for _, zone in self.map_read.zone.items():
            radius = 10
            color = (85, 118, 171)  # no metadata base_color
            pos_x = (zone.x * self.zoom) + (self.width // 4)
            pos_y = (zone.y * self.zoom) + (self.height // 4)
            dist_x = mousse_p[0] - pos_x
            dist_y = mousse_p[1] - pos_y
            if zone.metadata:  # metacolor
                try:
                    if zone.metadata.color == "rainbow":
                        rect_pos = rainbow_frame.get_rect(
                            center=(pos_x, pos_y))
                        self.screen.blit(rainbow_frame, rect_pos)
                        continue
                    else:
                        color = zone.metadata.color
                except ValueError:
                    pass  # color default
            # distance = √(dist_x² + dist_y²) hypot
            is_hooverd = math.hypot(dist_x, dist_y) < radius
            if is_hooverd:
                color = (85, 118, 171)
            py.draw.circle(self.screen, color, (pos_x, pos_y), 12)

# def draw_circle(self) -> None:
#         texture = py.image.load("circle_rainbow.png")
#         rainbow_texture = py.transform.scale(texture, (20, 20))
#         mousse_p = py.mouse.get_pos()
#         for _, zone in self.map_read.zone.items():
#             radius = 10
#             color = (85, 118, 171)  # no metadata base_color
#             pos_x = (zone.x * self.zoom) + (self.width // 4)
#             pos_y = (zone.y * self.zoom) + (self.height // 4)
#             dist_x = mousse_p[0] - pos_x
#             dist_y = mousse_p[1] - pos_y
#             if zone.metadata:  # metacolor
#                 try:
#                     if zone.metadata.color == "rainbow":
#                         rect_pos = rainbow_texture.get_rect(
#                             center=(pos_x, pos_y))
#                         self.screen.blit(rainbow_texture, rect_pos)
#                         continue
#                     else:
#                         color = zone.metadata.color
#                 except ValueError:
#                     pass  # color default
#             # distance = √(dist_x² + dist_y²) hypot
#             is_hooverd = math.hypot(dist_x, dist_y) < radius
#             if is_hooverd:
#                 color = (85, 118, 171)
#             py.draw.circle(self.screen, color, (pos_x, pos_y), 12)

    def start_sim(self) -> None:
        while self.running_mode:
            for event in py.event.get():
                if event.type == py.QUIT:
                    self.running_mode = False
                elif event.type == py.MOUSEMOTION:
                    self.mousse_position = event.pos
            self.width, self.height = self.screen.get_size()  # RESIZE
            self.screen.fill(self.BG_COLOR)
            self.draw_network()
            self.draw_circle()
            py.display.flip()
            self.clock_fps.tick(60)
        py.quit()

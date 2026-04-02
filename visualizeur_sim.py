from read_map import Reader
from typing import List
import pygame as py
import math
import os


class FrameCircle:
    def __init__(self, path: str, target_width: int, speed_frame: float = 5.5) -> None:
        self.path = path
        self.frames: List = []
        self.index_pos: int = 0
        self.count_frames: int = 0
        self.target_widht = target_width
        self.speed = speed_frame
        self.frames = self.load_frames()

    def load_frames(self) -> list:
        frames = []
        for f in sorted(os.listdir(self.path)):
            if f.endswith(".png") or f.endswith(".jpg"):
                img = py.image.load(os.path.join(self.path, f)).convert_alpha()
                get_bg_orbe = img.get_at((0, 0))
                img.set_colorkey(get_bg_orbe)  # black transparent
                ratio = img.get_width() / img.get_height()
                target = int(self.target_widht / ratio)
                img = py.transform.scale(img, (self.target_widht, target))
                # bruit gif
                tolerence = 30
                width, height = img.get_size()
                for x in range(width):
                    for y in range(height):
                        r, g, b, a = img.get_at((x, y))
                        if r < tolerence and g < tolerence and b < tolerence:
                            img.set_at((x, y), (r, g, b, 0))  # trasparant
                frames.append(img)
        return frames

    def update_frames(self) -> py.Surface:
        self.count_frames += 1
        if self.count_frames >= self.speed:
            self.count_frames = 0
            self.index_pos = (self.index_pos + 1) % len(self.frames)  # reset a 0
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
        self.zoom = 90
        self.BG_COLOR: tuple = ((30, 30, 46))  # cattpucin
        self.running_mode = True
        self.rainbow = FrameCircle("rainbow_texture", 45, speed_frame=2.5)
        self.green = FrameCircle("green_texture", 42, speed_frame=1.5)
        self.cam_x: int = 0
        self.cam_y: int = 0
        # self.default_color: tuple = ((30, 69, 41))

    def draw_network(self) -> None:
        for co in self.map_read.connection:
            z1 = self.map_read.zone[co.z_1]
            z2 = self.map_read.zone[co.z_2]
            start_hub = (
                (z1.x * self.zoom) + (self.width // 4) + self.cam_x,
                (z1.y * self.zoom) + (self.height // 4) + self.cam_y,
            )
            end_hub = (
                (z2.x * self.zoom) + (self.width // 4) + self.cam_x,
                (z2.y * self.zoom) + (self.height // 4) + self.cam_y,
            )
            py.draw.line(self.screen, "white", start_hub, end_hub, 2)

    def draw_circle(self) -> None:
        rainbow_frame = self.rainbow.update_frames()
        green_frame = self.green.update_frames()
        mousse_p = py.mouse.get_pos()
        for _, zone in self.map_read.zone.items():
            radius = 10
            color = (39, 69, 41)  # no metadata base_color
            pos_x = (zone.x * self.zoom) + (self.width // 4) + self.cam_x
            pos_y = (zone.y * self.zoom) + (self.height // 4) + self.cam_y
            dist_x = mousse_p[0] - pos_x
            dist_y = mousse_p[1] - pos_y
            if zone.metadata:
                try:
                    if zone.metadata.color == "rainbow":
                        offset_x = 15  # +10 == r -10 == l
                        offset_y = 2  # +10 down -10 up
                        rect_pos_rainbow = rainbow_frame.get_rect(
                            center=(pos_x + offset_x, pos_y + offset_y))
                        self.screen.blit(
                            rainbow_frame,
                            rect_pos_rainbow)
                        continue
                    elif zone.metadata.color == "green":
                        offset_x = -10  # reculer le cercle
                        offset_y = 0
                        rect_pos_green = green_frame.get_rect(
                            center=(pos_x + offset_x, pos_y - offset_y))
                        self.screen.blit(
                            green_frame,
                            rect_pos_green,
                            special_flags=py.BLEND_ADD)  # blend particule
                        continue
                    else:
                        if zone.metadata.color in py.color.THECOLORS:
                            color = zone.metadata.color
                except ValueError:
                    pass  # si non color default
            # distance = √(dist_x² + dist_y²) hypot
            is_hooverd = math.hypot(dist_x, dist_y) < radius
            if is_hooverd:
                color = (85, 118, 171)
            py.draw.circle(self.screen, color, (pos_x, pos_y), 12)

    def start_sim(self) -> None:
        is_drag = False
        try:
            print("Pressed (CRTL + C) to interrupt program")
            while self.running_mode:
                for event in py.event.get():
                    if event.type == py.QUIT:
                        self.running_mode = False
                    # 1 == click_left
                    elif event.type == py.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            mouse_x, mouse_y = event.pos
                            is_drag = True
                            offset_x = self.cam_x - mouse_x
                            offset_y = self.cam_y - mouse_y
                    elif event.type == py.MOUSEBUTTONUP:
                        if event.button == 1:
                            is_drag = False
                    elif event.type == py.MOUSEWHEEL:
                        self.zoom += event.y * 5
                        if self.zoom < 5:
                            self.zoom = 5
                    elif event.type == py.MOUSEMOTION:
                        if is_drag:
                            mouse_x, mouse_y = event.pos
                            self.cam_x = mouse_x + offset_x
                            self.cam_y = mouse_y + offset_y
                        self.mousse_position = event.pos
                self.width, self.height = self.screen.get_size()  # RESIZE
                self.screen.fill(self.BG_COLOR)
                self.draw_network()
                self.draw_circle()
                py.display.flip()
                self.clock_fps.tick(60)
            py.quit()
        except KeyboardInterrupt:
            print('\n\nProgram terminated by User')

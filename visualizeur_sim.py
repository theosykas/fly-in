from read_map import Reader
from typing import List
import pygame as py
from solver import Solver
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
            if f.endswith(".png"):
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
                        r, g, b, _ = img.get_at((x, y))
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
        icon = py.image.load("icon.png")
        py.display.set_icon(icon)
        self.zoom: float = 90.0
        self.scroll_speed: float = 8.0
        self.BG_COLOR: tuple = ((30, 30, 46))  # cattpucin
        self.running_mode = True
        self.rainbow = FrameCircle("rainbow_texture", 45, speed_frame=2.5)
        self.green = FrameCircle("green_texture", 42, speed_frame=1.5)
        self.cam_x: float = 0.0
        self.cam_y: float = 0.0
        self.drone_img = py.image.load("drone.png").convert_alpha()
        self.drone_img = py.transform.scale(self.drone_img, (30, 30))
        self.solver = None
        self.current_turn: int = 0
        self.sim_solve: bool = False

    def draw_drone(self):
        for drone in self.map_read.drones:
            if drone.current_zone not in self.map_read.zone:
                continue
            zone = self.map_read.zone[drone.current_zone]
            draw_x = (zone.x * self.zoom) + (self.width // 4) + self.cam_x
            draw_y = (zone.y * self.zoom) + (self.height // 4) + self.cam_y
            rect_drone = self.drone_img.get_rect(center=(int(draw_x),
                                                         int(draw_y)))
            self.screen.blit(self.drone_img, rect_drone)

    def start_solve(self):
        self.solver = Solver(self.map_read)
        self.solver.init_drone()
        self.current_turn = 0
        self.sim_solve = True

    def draw_network(self) -> None:
        line_zoom = max(2, int(2 * self.zoom / 90.0))
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
            py.draw.line(self.screen, (183, 189, 248),
                         start_hub, end_hub, line_zoom)

    def draw_circle(self) -> None:
        rainbow_frame = self.rainbow.update_frames()
        green_frame = self.green.update_frames()
        mousse_p = py.mouse.get_pos()
        zoom_avg = self.zoom / 90.0
        radius_dynamic = max(5, int(12 * (zoom_avg)))
        for _, zone in self.map_read.zone.items():
            color = (39, 69, 41)  # no metadata base_color / olive
            pos_x = (zone.x * self.zoom) + (self.width // 4) + self.cam_x
            pos_y = (zone.y * self.zoom) + (self.height // 4) + self.cam_y
            dist_x = mousse_p[0] - pos_x
            dist_y = mousse_p[1] - pos_y
            if zone.metadata:
                try:
                    if zone.metadata.color == "rainbow":
                        offset_x = 15.0 * zoom_avg  # +10 == r -10 == l
                        offset_y = 2.0 * zoom_avg  # +10 down -10 up
                        tarck_frame = max(5, int(self.rainbow.target_widht
                                          * zoom_avg))  # sync zoom et img
                        scaled_frame = py.transform.scale(rainbow_frame,
                                                          (tarck_frame,
                                                           tarck_frame))
                        rect_pos_rainbow = scaled_frame.get_rect(  # centrer .png
                            center=(pos_x + offset_x, pos_y + offset_y))
                        self.screen.blit(
                            scaled_frame,
                            rect_pos_rainbow)
                        continue
                    elif zone.metadata.color == "green":
                        track_frame = max(5, int(self.green.target_widht
                                                 * zoom_avg))
                        scale_green = py.transform.scale(green_frame,
                                                         (track_frame,
                                                          track_frame))
                        rect_pos_green = scale_green.get_rect(
                            center=(int(pos_x), int(pos_y)))
                        self.screen.blit(
                            scale_green,
                            rect_pos_green,
                            special_flags=py.BLEND_ADD)  # blend particule
                        continue
                    else:
                        if zone.metadata.color in py.color.THECOLORS:
                            color = zone.metadata.color
                except ValueError:
                    pass  # si non color default
            # distance = √(dist_x² + dist_y²) hypot
            is_hooverd = math.hypot(dist_x, dist_y) < radius_dynamic
            if is_hooverd:
                color = (85, 118, 171)
            py.draw.circle(self.screen, color, (pos_x, pos_y), radius_dynamic)

    def start_sim(self) -> None:
        is_drag = False
        self.start_solve()
        last_move = py.time.get_ticks()
        move_delay = 500
        try:
            print("Pressed (CRTL + C) to interrupt program")
            while self.running_mode:
                current_time = py.time.get_ticks()
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
                        mouse_x, mouse_y = py.mouse.get_pos()
                        adj_pos_x = mouse_x - (self.width // 4)
                        adj_pos_y = mouse_y - (self.height // 4)
                        x_pos = (adj_pos_x - self.cam_x) / self.zoom
                        y_pos = (adj_pos_y - self.cam_y) / self.zoom
                        self.zoom += event.y * 5 * self.scroll_speed  # aug speed
                        self.zoom = max(5, self.zoom)  # -- zoom (max)
                        self.zoom = min(445.0, self.zoom)  # ++ zoom
                        self.cam_x = adj_pos_x - (x_pos * self.zoom)
                        self.cam_y = adj_pos_y - (y_pos * self.zoom)  # track et re calcule
                    elif event.type == py.MOUSEMOTION:
                        if is_drag:
                            mouse_x, mouse_y = event.pos
                            self.cam_x = mouse_x + offset_x
                            self.cam_y = mouse_y + offset_y
                        self.mousse_position = event.pos
                if self.sim_solve and (current_time - last_move >
                                       move_delay):
                    moving = self.solver.turn()
                    self.current_turn += 1
                    last_move = current_time
                    if not moving:
                        self.sim_solve = False
                self.width, self.height = self.screen.get_size()  # RESIZE
                self.screen.fill(self.BG_COLOR)
                self.draw_network()
                self.draw_circle()
                self.draw_drone()
                py.display.flip()
                self.clock_fps.tick(60)
            py.quit()
        except KeyboardInterrupt:
            print('\n\nProgram terminated by User')

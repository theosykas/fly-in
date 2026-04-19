from typing import List, Optional, Union
from read_map import Reader
from solver import Solver
import pygame as py
import math
import os


class FrameCircle:
    def __init__(self, path: str, target_width: int,
                 speed_frame: float = 5.5) -> None:
        """
        Initializes the animated frame sequence from a directory of PNG images.

        Args:
            path (str): Path to the directory containing PNG frame images.
            target_width (int): Target width in pixels for scaling the frames.
            speed_frame (float): Number of ticks between frame updates.
            Defaults to 5.5.

        Attributes:
            path (str): Path to the frames directory.
            frames (List[py.Surface]): List of loaded and processed pygame
            surfaces.
            index_pos (int): Current frame index. Defaults to 0.
            count_frames (int): Internal tick counter for animation speed.
            Defaults to 0.
            target_widht (int): Target width used for scaling.
            speed (float): Number of ticks between frame updates.
        """
        self.path = path
        self.frames: List[py.Surface] = []
        self.index_pos: int = 0
        self.count_frames: int = 0
        self.target_widht = target_width
        self.speed = speed_frame
        self.frames = self.load_frames()

    def load_frames(self) -> list[py.Surface]:
        """
        Loads, scales, and processes all PNG frames from the instance path
        directory.

        Returns:
            List[py.Surface]: List of processed pygame surfaces with
            transparency
            applied.
        """
        frames = []
        for f in sorted(os.listdir(self.path)):
            if f.endswith(".png"):
                img = py.image.load(os.path.join(self.path, f)).convert_alpha()
                get_bg_orbe = img.get_at((0, 0))
                img.set_colorkey(get_bg_orbe)  # black transparent
                ratio = img.get_width() / img.get_height()
                target = int(self.target_widht / ratio)
                img = py.transform.scale(img, (self.target_widht, target))
                tolerence = 30
                width, height = img.get_size()
                for x in range(width):
                    for y in range(height):
                        r, g, b, _ = img.get_at((x, y))
                        if r < tolerence and g < tolerence and b < tolerence:
                            img.set_at((x, y), (r, g, b, 0))
                frames.append(img)
        return frames

    def update_frames(self) -> py.Surface:
        """
        Advances the animation by one tick and returns the current frame
        surface.

        Returns:
            py.Surface: The current frame surface at the updated animation
            index.
        """
        self.count_frames += 1
        if self.count_frames >= self.speed:
            self.count_frames = 0
            self.index_pos = (self.index_pos + 1) % len(self.frames)
        return self.frames[self.index_pos]


class Visualizeur:
    def __init__(self, width: int, height: int, map_read: Reader) -> None:
        """
    Initializes the pygame visualization window and all rendering components.

    Args:
        width (int): Initial window width in pixels.
        height (int): Initial window height in pixels.
        map_read (Reader): Parsed map data containing zones, connections and
        drones.

    Attributes:
        height (int): Current window height.
        width (int): Current window width.
        map_read (Reader): Reference to the parsed map data.
        screen (py.Surface): Main pygame display surface.
        clock_fps (py.time.Clock): Clock used to cap frame rate.
        zoom (float): Current zoom level. Defaults to 90.0.
        scroll_speed (float): Zoom sensitivity on scroll. Defaults to 8.0.
        BG_COLOR (tuple[int, int, int]): Background color. Defaults to
        (30, 30, 46).
        running_mode (bool): Whether the main loop is active. Defaults to True.
        rainbow (FrameCircle): Animated rainbow texture for special zones.
        green (FrameCircle): Animated green texture for special zones.
        cam_x (float): Horizontal camera offset. Defaults to 0.0.
        cam_y (float): Vertical camera offset. Defaults to 0.0.
        drone_img (py.Surface): Scaled drone sprite image.
        solver (Optional[Solver]): Solver instance, set on simulation start.
        Defaults to None.
        current_turn (int): Current simulation turn counter. Defaults to 0.
        sim_solve (bool): Whether the simulation is currently running.
        Defaults to False.
        font (py.font.Font): Font used for HUD rendering.
        font_x (int): Horizontal position of the HUD text. Defaults to 9.
        font_y (int): Vertical position of the HUD text. Defaults to 9.
    """
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
        self.BG_COLOR: tuple[int, int, int] = ((30, 30, 46))
        self.running_mode = True
        self.rainbow = FrameCircle("rainbow_texture", 45, speed_frame=2.5)
        self.green = FrameCircle("green_texture", 42, speed_frame=1.5)
        self.cam_x: float = 0.0
        self.cam_y: float = 0.0
        self.drone_img = py.image.load("drone.png").convert_alpha()
        self.drone_img = py.transform.scale(self.drone_img, (30, 30))
        self.solver: Optional[Solver] = None
        self.current_turn: int = 0
        self.sim_solve: bool = False
        py.font.init()
        self.font = py.font.SysFont("Consolas", 15)
        self.font_x = 9
        self.font_y = 9

    def draw_drone(self) -> None:
        """
        Draws all drones on screen at their current zone positions.
        """
        for drone in self.map_read.drones:
            if drone.current_zone not in self.map_read.zone:
                continue
            zone = self.map_read.zone[drone.current_zone]
            draw_x = (zone.x * self.zoom) + (self.width // 4) + self.cam_x
            draw_y = (zone.y * self.zoom) + (self.height // 4) + self.cam_y
            rect_drone = self.drone_img.get_rect(center=(int(draw_x),
                                                         int(draw_y)))
            self.screen.blit(self.drone_img, rect_drone)

    def start_solve(self) -> None:
        """
        Initializes the solver, places drones at their starting positions
        and begins the simulation.
        """
        self.solver = Solver(self.map_read)
        self.solver.init_drone()
        self.current_turn = 0
        self.sim_solve = True

    def draw_network(self) -> None:
        """
        Draws all connections between zones, highlighting active
        connections with drones in transit.
        """
        line_zoom = max(2, int(2 * self.zoom / 90.0))
        for co in self.map_read.connection.values():
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
            if co.drones_transit:
                color = (101, 143, 112)
            else:
                color = (183, 189, 248)
            py.draw.line(self.screen, color,
                         start_hub, end_hub, line_zoom)

    def draw_circle(self) -> None:
        """
        Draws all zones as circles, applying special textures or
        colors based on zone metadata.
        """
        rainbow_frame = self.rainbow.update_frames()
        green_frame = self.green.update_frames()
        mousse_p = py.mouse.get_pos()
        zoom_avg = self.zoom / 90.0
        radius_dynamic = max(5, int(12 * (zoom_avg)))
        for _, zone in self.map_read.zone.items():
            color: Union[tuple[int, int, int], str] = (39, 69, 41)
            pos_x = (zone.x * self.zoom) + (self.width // 4) + self.cam_x
            pos_y = (zone.y * self.zoom) + (self.height // 4) + self.cam_y
            dist_x = mousse_p[0] - pos_x
            dist_y = mousse_p[1] - pos_y
            if zone.metadata:
                try:
                    if zone.metadata.color == "rainbow":
                        offset_x = 15.0 * zoom_avg
                        offset_y = 2.0 * zoom_avg
                        tarck_frame = max(5, int(self.rainbow.target_widht
                                          * zoom_avg))
                        if isinstance(green_frame, py.Surface):
                            scaled_frame = py.transform.scale(rainbow_frame,
                                                              (tarck_frame,
                                                               tarck_frame))
                            rect_pos_rainbow = scaled_frame.get_rect(
                                center=(pos_x + offset_x, pos_y + offset_y))
                            self.screen.blit(
                                scaled_frame,
                                rect_pos_rainbow)
                            continue
                    elif zone.metadata.color == "green":
                        track_frame = max(5, int(self.green.target_widht
                                                 * zoom_avg))
                        if isinstance(green_frame, py.Surface):
                            scale_green = py.transform.scale(green_frame,
                                                             (track_frame,
                                                              track_frame))
                            rect_pos_green = scale_green.get_rect(
                                center=(int(pos_x), int(pos_y)))
                            self.screen.blit(
                                scale_green,
                                rect_pos_green,
                                special_flags=py.BLEND_ADD)
                            continue
                    else:
                        if zone.metadata.color in py.color.THECOLORS:
                            color = zone.metadata.color
                except ValueError:
                    pass
            is_hooverd = math.hypot(dist_x, dist_y) < radius_dynamic
            if is_hooverd:
                color = (85, 118, 171)
            py.draw.circle(self.screen, color, (pos_x, pos_y), radius_dynamic)

    def format_output(self, current_time: int, last_move:
                      int, move_delay: int) -> int:
        """
        Advances the simulation by one turn if the move delay has elapsed and
        prints the result.

        Args:
            current_time (int): Current pygame tick timestamp in milliseconds.
            last_move (int): Pygame tick timestamp of the last move in
            milliseconds.
            move_delay (int): Minimum delay between moves in milliseconds.

        Returns:
            int: Updated last_move timestamp if a move occurred, otherwise the
            unchanged last_move.
        """
        if self.sim_solve and current_time - last_move > move_delay:
            assert self.solver is not None
            if len(self.solver.is_finished) < len(self.map_read.drones):
                moving, output_format = self.solver.turn()
                if output_format:
                    print(output_format)
                    self.current_turn += 1
                if not moving:
                    self.sim_solve = False
                if len(self.solver.is_finished) >= len(self.map_read.drones):
                    return current_time
            return current_time
        return last_move

    def counter_score(self, height: int, widht: int) -> py.Surface:
        """
        Renders and draws the current turn counter onto the screen.

        Args:
            height (int): Horizontal position of the turn counter text.
            widht (int): Vertical position of the turn counter text.

        Returns:
            py.Surface: The rendered text surface.
        """
        font_blit = self.font.render(f"turns {self.current_turn}",
                                     True, (101, 143, 112))
        self.screen.blit(font_blit, (height, widht))
        return font_blit

    def start_sim(self) -> None:
        """
        Starts the main pygame event loop, handling input, rendering and
        simulation advancement.

        Raises:
            KeyboardInterrupt: Caught internally to allow graceful termination
            via CTRL+C.
        """
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
                        self.zoom += event.y * 5 * self.scroll_speed
                        self.zoom = max(5, self.zoom)
                        self.zoom = min(445.0, self.zoom)
                        self.cam_x = adj_pos_x - (x_pos * self.zoom)
                        self.cam_y = adj_pos_y - (y_pos * self.zoom)
                    elif event.type == py.MOUSEMOTION:
                        if is_drag:
                            mouse_x, mouse_y = event.pos
                            self.cam_x = mouse_x + offset_x
                            self.cam_y = mouse_y + offset_y
                        self.mousse_position = event.pos
                last_move = self.format_output(current_time=current_time,
                                               last_move=last_move,
                                               move_delay=move_delay)
                self.width, self.height = self.screen.get_size()
                self.screen.fill(self.BG_COLOR)
                self.draw_network()
                self.draw_circle()
                self.draw_drone()
                self.counter_score(self.font_x, self.font_y)
                py.display.flip()
                self.clock_fps.tick(60)
            py.quit()
        except KeyboardInterrupt:
            print('\n\nProgram terminated by User')

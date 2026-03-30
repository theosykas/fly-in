from read_map import Zone, Connection, Reader
import pygame
import math


class InitWindow:
    def __init__(self, height: int, width: int, map_r: Reader) -> None:
        pygame.init()
        # self.mousse_position = (0, 0)
        self.height = height
        self.width = width
        self.map_r = map_r
        self.screen = pygame.display.set_mode((self.height, self.width))  # tuple set_mode
        self.clock_fps = pygame.time.Clock()
        pygame.display.set_caption("FLY-IN")
        self.zoom = 50
        self.BG_COLOR: str = "grey0"
        self.running_mode = True

    def draw_network(self) -> None:
        for co in self.map_r.connection:
            z1 = self.map_r.zone[co.z_1]
            z2 = self.map_r.zone[co.z_2]
            start_pos = (
                        (z1.x * self.zoom) + (self.width // 4),
                        (z1.y * self.zoom) + (self.height // 4)
                        )
            end_pos = (
                    (z2.x * self.zoom) + (self.width // 4),
                    (z2.y * self.zoom) + (self.height // 4)
                    )
            pygame.draw.line(self.screen,
                             "white",
                             start_pos,
                             end_pos,
                             2)

    def draw_circle(self) -> None:
        for _, zone in self.map_r.zone.items():
            mousse_p = pygame.mouse.get_pos()
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
            pygame.draw.circle(self.screen,
                               color,
                               (pos_x, pos_y),
                               10)

    def start_sim(self) -> None:
        while self.running_mode:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running_mode = False
                elif event.type == pygame.MOUSEMOTION:
                    self.mousse_position = event.pos
            self.screen.fill(self.BG_COLOR)
            self.draw_network()
            self.draw_circle()
            pygame.display.flip()
            self.clock_fps.tick(60)
        pygame.quit()

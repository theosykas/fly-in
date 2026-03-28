import pygame


class InitWindow:
    def __init__(self, height: int, width: int) -> None:
        pygame.init()
        self.height = height
        self.width = width
        self.screen = pygame.display.set_mode((self.height, self.width))  # tuple set_mode
        self.clock_fps = pygame.time.Clock()
        pygame.display.set_caption("FLY-IN")
        self.running_mode = True

    def start_sim(self) -> None:
        while self.running_mode:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running_mode = False
            self.screen.fill("grey0")
            pygame.display.flip()
            self.clock_fps.tick(60)
    pygame.quit()

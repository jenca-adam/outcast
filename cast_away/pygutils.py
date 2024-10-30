import pygame
from .fonts import HELVETICA_XSMALL

class ProgressBar:
    def __init__(self, screen, total, pb_width=250, pb_height=20):
        self.total = total
        self.current = 0
        self.screen = screen
        self.sw,self.sh=sw, sh = screen.get_size()
        
        self.pb_width = pb_width
        self.pb_height = pb_height
        self.top, self.left = sh // 2 - pb_height // 2, sw // 2 - pb_width // 2
        pygame.draw.rect(
            screen,
            (128, 128, 128),
            pygame.Rect(self.left, self.top, pb_width, pb_height),
            10,
        )
        self.label_surface=pygame.surface.Surface((sw,20))
        pygame.display.flip()

    def partial_iter(self, it, pb_width=250, pb_height=20):
        for i in it:
            self.current += 1
            si=str(i)
            label_size = HELVETICA_XSMALL.size(si)
            label = HELVETICA_XSMALL.render(si, True, (255,255,255))
            self.label_surface.fill((0,0,0))
            self.label_surface.blit(label, (self.sw/2-label_size[0]/2, 0))
            self.screen.blit(self.label_surface, (0,self.top - 30))
            yield i
            pygame.draw.rect(
                self.screen,
                (255, 255, 255),
                pygame.Rect(
                    self.left,
                    self.top,
                    (self.current) * self.pb_width / self.total,
                    self.pb_height,
                ),
            )
            pygame.display.flip()
        if self.current >= self.total:
            self.screen.fill((0, 0, 0))
            pygame.display.flip()

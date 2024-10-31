import pygame
from . import helpers
from . import loader
class Crosshair(pygame.sprite.Sprite):
    def __init__(self,screen, clamp_rect):
        super().__init__()
        self.image=loader.IMAGES["crosshair.png"]
        self.screen=screen
        self.clamp_rect = clamp_rect
        self.center = helpers.get_center(screen)
        self._size = self.image.get_size()
        self.rect = (self.center[0]-self._size[0]//2, self.center[1]-self._size[1]//2)

    def mousemotion_handler(self, event):
        center=event.pos
        nrect=(center[0]-self._size[0]//2, center[1]-self._size[1]//2, *self._size)
        print(nrect)
        if self.clamp_rect.contains(nrect):
            self.rect=nrect[:2]
            self.center=center

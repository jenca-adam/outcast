import pygame
from .settings import BULLET_SPEED, BULLET_LIFETIME
from . import helpers
from . import loader


class Crosshair(pygame.sprite.Sprite):
    def __init__(self, screen, clamp_rect):
        super().__init__()
        self.image = loader.IMAGES["crosshair.png"]
        self.screen = screen
        self.clamp_rect = clamp_rect
        self.center = helpers.get_center(screen)
        self._size = self.image.get_size()
        self.rect = (
            self.center[0] - self._size[0] // 2,
            self.center[1] - self._size[1] // 2,
        )

    def mousemotion_handler(self, event):
        center = event.pos
        nrect = (
            center[0] - self._size[0] // 2,
            center[1] - self._size[1] // 2,
            *self._size,
        )
        if self.clamp_rect.contains(nrect):
            self.rect = nrect[:2]
            self.center = center


class Bullet:
    def __init__(self, scene, origin, direction, engine, target=None):
        self.position = origin
        self.target = target
        self.direction = direction.normalized()
        self.direction.z = -self.direction.z
        self.direction.y = (self.direction.y + 0.5) * 2
        self.direction.x = self.direction.x * 1.5
        # self.direction=renderer.vec3.Vec3(0,0,1)
        print(self.direction)
        self.scene = scene
        self.object = loader.MODELS["bullet"].clone()
        self.object.translate(self.position - self.object.calculate_centerpoint())
        self.scene.add_obj(self.object)
        self.engine = engine

    def _tick(self, engine):
        self.position += self.direction * BULLET_SPEED * engine.delta
        self.object.translate(self.direction * BULLET_SPEED * engine.delta)
        engine.update()

    def fire(self):
        self.engine.update()
        self.engine.until(BULLET_LIFETIME, self._tick)
        self.engine.after(BULLET_LIFETIME, self.destroy)

    def destroy(self, engine):
        self.scene.objects.remove(self.object)
        engine.update()

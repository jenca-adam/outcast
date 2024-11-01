import pygame
import pygame_gui
import random
from .settings import BULLET_SPEED, BULLET_LIFETIME, BULLET_DMG, SHIP_MOVE_SPEED, PIXEL_SIZE
from . import helpers
from . import loader
from . import renderer

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

class Enemy:
    def __init__(self, hp, obj, engine, kill_event):
        self.hp = hp
        self.engine = engine
        self.object = obj
        self.kill_event = kill_event
        self.maxhp = hp
        self.health_bar=pygame_gui.elements.UIStatusBar((0,0,200,20), percent_method=self.get_health_percentage, manager=engine.uimgr)
    def get_health_percentage(self, *_):
        return 100*self.hp/self.maxhp
    def move_health_bar(self, *_):
        hbpos= (self.object._projection_x_viewport @ self.object.centerpoint)*PIXEL_SIZE+renderer.vec3.Vec3(*self.engine.scene_offset,0)+renderer.vec3.Vec3(-100,-70,0)
        self.health_bar.rect = self.health_bar.rect.move_to(x=hbpos.x, y=hbpos.y)
    def loop(self, *_):
        self.engine.until(
            300,
            helpers.translate_object(
                self.object,
                renderer.vec3.Vec3(
                    random.randrange(-10, 11) *SHIP_MOVE_SPEED,
                    random.randrange(-10, 11) *SHIP_MOVE_SPEED,
                    random.randrange(-10, 11) *SHIP_MOVE_SPEED,
                ),
                clamp_top=0,
                clamp_bottom=8,
                clamp_left=-5,
                clamp_right=1,
                clamp_front=10,
                clamp_back=20,
            ),
        )
        self.engine.until(300, self.move_health_bar)
        self.engine.after(300, self.loop)

    def hit(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.kill_event(self)


class Bullet:
    def __init__(self, scene, origin, direction, engine, target):
        self.position = origin
        self.target = target
        self.direction = direction.normalized()
        self.direction.z = -self.direction.z
        self.direction.y = (self.direction.y + 0.5) *2
        self.direction.x = self.direction.x * 1.5
        # self.direction=renderer.vec3.Vec3(0,0,1)
        print(self.direction)
        self.scene = scene
        self.object = loader.MODELS["bullet"].clone()
        self.object.translate(self.position - self.object.calculate_centerpoint())
        self.scene.add_obj(self.object)
        self.engine = engine
        self.alive=True
    def _tick(self, engine):
        if not self.alive:
            return
        self.position += self.direction * BULLET_SPEED * engine.delta
        self.object.translate(self.direction * BULLET_SPEED * engine.delta)
        if self.target.object.bbox.collides_with(self.position):
            self.target.hit(BULLET_DMG)
            self.destroy(self.engine)
        engine.update()

    def fire(self):
        self.engine.update()
        self.engine.until(BULLET_LIFETIME, self._tick)
        self.engine.after(BULLET_LIFETIME, self.destroy)

    def destroy(self, engine):
        if not self.alive:
            return 
        self.alive=False
        self.scene.objects.remove(self.object)
        engine.update()

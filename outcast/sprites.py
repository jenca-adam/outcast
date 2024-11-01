import pygame
import pygame_gui
import random
from .settings import (
    BULLET_SPEED,
    BULLET_LIFETIME,
    BULLET_DMG,
    SHIP_MOVE_SPEED,
    PIXEL_SIZE,
    ASTEROID_HTK,
)
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
        self.alive = True
        self.health_bar = pygame_gui.elements.UIStatusBar(
            (0, 0, 200, 20),
            percent_method=self.get_health_percentage,
            manager=engine.uimgr,
        )

    def kill(self):
        self.alive = False
        self.health_bar.kill()
        self.engine.until(
            1500,
            helpers.rotate_object(
                self.object,
                renderer.vec3.Vec3(
                    random.randrange(360),
                    random.randrange(360),
                    random.randrange(360),
                ),
            ),
            use_offset=False,
        )
        self.engine.until(
            1500,
            helpers.translate_object(self.object, renderer.vec3.Vec3(0, 5, -10)),
            use_offset=False,
        )
        self.engine.after(
            1500, lambda engine: engine.scene_3d.objects.remove(self.object)
        )

    def get_health_percentage(self, *_):
        if not self.alive:
            return 0
        return max(0, 100 * self.hp / self.maxhp)

    def move_health_bar(self, *_):
        hbpos = (
            (self.object._projection_x_viewport @ self.object.centerpoint) * PIXEL_SIZE
            + renderer.vec3.Vec3(*self.engine.scene_offset, 0)
            + renderer.vec3.Vec3(-100, -70, 0)
        )
        self.health_bar.rect = self.health_bar.rect.move_to(x=hbpos.x, y=hbpos.y)

    def loop(self, *_):
        self.engine.reset_wait_time()
        if not self.alive:
            return
        self.engine.until(
            300,
            helpers.translate_object(
                self.object,
                renderer.vec3.Vec3(
                    random.randrange(-10, 11) * SHIP_MOVE_SPEED,
                    random.randrange(-10, 11) * SHIP_MOVE_SPEED,
                    random.randrange(-10, 11) * SHIP_MOVE_SPEED,
                ),
                clamp_top=0,
                clamp_bottom=8,
                clamp_left=-5,
                clamp_right=1,
                clamp_front=10,
                clamp_back=20,
            ),
            use_offset=False,
        )
        self.engine.until(300, self.move_health_bar, use_offset=False)
        self.engine.after(300, self.loop)

    def hit(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.kill_event(self)


class Asteroid:
    def __init__(self, engine, kill_event, old_age_event):
        self.engine = engine
        self.hp = ASTEROID_HTK * BULLET_DMG
        self.object = loader.MODELS["rock"].clone(True)
        self.kill_event = kill_event
        self.old_age_event = old_age_event
        self.alive = True
        self.object.translate(
            renderer.vec3.Vec3(
                random.randrange(-10, 11) / 10,
                random.randrange(-10, 11) / 10,
                random.randrange(-10, 11) / 10,
            )
        )
        if random.randrange(2):
            self.object.translate(renderer.vec3.Vec3(20, 0, 0))

    def hit(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.kill_event(self)

    def kill(self, *_):
        self.alive = False
        self.engine.until(
            1500,
            helpers.translate_object(self.object, renderer.vec3.Vec3(0, 0, -10)),
            use_offset=False,
        )
        # rotation is already done so
        self.engine.after(1500, self.die_of_old_age)

    def die_of_old_age(self, *_):
        if self.object in self.engine.scene_3d.objects:
            self.engine.scene_3d.objects.remove(self.object)
            self.object.cleanup()
        if self.alive:
            self.alive = False
            self.old_age_event(self)

    def loop(self):
        self.engine.until(
            5000,
            helpers.translate_object(
                self.object, renderer.vec3.Vec3(0, 0, random.randrange(18, 36))
            ),
            use_offset=False,
        )
        self.engine.until(
            5000,
            helpers.rotate_object(
                self.object,
                renderer.vec3.Vec3(
                    random.randrange(360), random.randrange(360), random.randrange(360)
                ),
            ),
            use_offset=False,
        )
        self.engine.after(5000, self.die_of_old_age)
        self.engine.scene_3d.add_obj(self.object)
        self.engine.update()


class Bullet:
    def __init__(self, scene, origin, direction, engine, targets, score_counter):
        self.position = origin
        self.targets = targets
        self.score_counter = score_counter
        self.direction = direction.normalized()
        self.direction.z = -self.direction.z
        self.direction.y = (self.direction.y + 0.5) * 2
        self.direction.x = self.direction.x * 1.5
        # self.direction=renderer.vec3.Vec3(0,0,1)
        # print(self.direction)
        self.scene = scene
        self.object = loader.MODELS["bullet"].clone(True)
        self.object.translate(self.position - self.object.calculate_centerpoint())
        self.scene.add_obj(self.object)
        self.engine = engine
        self.alive = True

    def _tick(self, engine):
        if not self.alive:
            return
        self.position += self.direction * BULLET_SPEED * engine.delta
        self.object.translate(self.direction * BULLET_SPEED * engine.delta)
        for target in self.targets:  # O(n)
            if target.alive and target.object.bbox.collides_with(self.position):
                target.hit(BULLET_DMG)
                qpos = (
                    self.object._projection_x_viewport @ self.position
                ) * PIXEL_SIZE + renderer.vec3.Vec3(*engine.scene_offset, 0)

                self.score_counter.update_score(1, (qpos.x, qpos.y))
                self.destroy(self.engine)  # only hit once? idk it doesnt matter
                break
        engine.update()

    def fire(self):
        self.engine.update()
        self.engine.until(BULLET_LIFETIME, self._tick, use_offset=False)
        self.engine.after(BULLET_LIFETIME, self.destroy)

    def destroy(self, engine):
        if not self.alive:
            return
        self.alive = False
        self.scene.objects.remove(self.object)
        engine.update()

import pygame
import pygame_gui
import random
from pygame_gui.core import ObjectID
from .settings import *
from . import renderer
from . import loader
from . import helpers
from . import sprites
SEGMENTS = {}


def add_segment(segment_name):
    def decorator(function):
        SEGMENTS[segment_name] = function
        return function

    return decorator


@add_segment("intro")
def _segment_intro(engine):
    engine.scene_3d.objects = []
    horn = loader.MODELS["horn"]
    announcement = loader.SOUNDS["announcement.mp3"]
    music = loader.SOUNDS["theme_violin.mp3"]
    buildup = loader.SOUNDS["buildup.mp3"]
    titlefont = loader.FONTS[("airstrikeacad.ttf", 96)]
    engine.scene_3d.add_obj(horn)
    announcement.play()
    engine.wait(500)
    engine.until(21500, helpers.rotate_object(horn, renderer.vec3.Vec3(0, 167.441, 0)))
    engine.after(6000, lambda engine: buildup.play())
    engine.until(2000, helpers.translate_object(horn, renderer.vec3.Vec3(0, 0, -1)))
    engine.wait(20000)
    engine.after(0, lambda engine: music.play())
    engine.after(0, lambda engine: buildup.fadeout(2000))
    engine.until(8000, helpers.translate_object(horn, renderer.vec3.Vec3(0, 0, -0.09)))
    engine.wait(6000)

    engine.until(
        4000,
        helpers.fadein_text(
            "CAST AWAY",
            titlefont,
            2.5,
            (0, 128, 128),
            helpers.get_center(engine.screen),
        ),
    )
    # engine.after(0, lambda engine:music.fadeout(4000))
    engine.wait(4000)  # block until the end
    engine.after(0, lambda engine: play_segment("destination_select", engine))


@add_segment("destination_select")
def _segment_destination_select(engine):
    def destination_select_button_handler(event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_object_id in (
            "#kepler",
            "#gliese",
            "#proxima",
        ):
            engine["target"] = event.ui_object_id
            engine.remove_ui_event_handler("dest_butt")
            kepler_button.kill()
            gliese_button.kill()
            proxima_button.kill()
            label.kill()
            loader.SOUNDS["theme_violin.mp3"].fadeout(2000)
            play_segment("main_game_intro", engine)

    engine.scene_3d.objects = []
    engine.update()
    label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((0, -500), (-1, -1)),
        text="Select a destination to flee to:",
        anchors={"center": "center"},
        manager=engine.uimgr,
        object_id=ObjectID(object_id="#select_label", class_id="@pixelated"),
    )
    kepler_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((-250, 0), (-1, 50)),
        text="KEPLER 1649C",
        anchors={"center": "center"},
        manager=engine.uimgr,
        object_id=ObjectID(object_id="#kepler", class_id="@pixelated"),
    )
    gliese_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((-25, 0), (-1, 50)),
        text="GLIESE 6677CC",
        anchors={"center": "center"},
        manager=engine.uimgr,
        object_id=ObjectID(object_id="#gliese", class_id="@pixelated"),
    )

    proxima_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((250, 0), (-1, 50)),
        text="PROXIMA CENTAURI B",
        anchors={"center": "center"},
        manager=engine.uimgr,
        object_id=ObjectID(object_id="#proxima", class_id="@pixelated"),
    )
    engine.add_ui_event_handler(destination_select_button_handler, "dest_butt")


@add_segment("main_game_intro")
def _segment_main_game_intro(engine):
    engine.scene_3d.set_kwargs(backface_culling=False)  # dirty fix
    engine.scene_3d.objects = []
    enemy_ship = loader.MODELS["enemy_ship"]
    police_siren = loader.SOUNDS["police-siren.mp3"]
    metal = loader.SOUNDS["metal.mp3"]
    metal.play()
    runfont = loader.FONTS[("airstrikeacad.ttf", 96)]
    police_siren.set_volume(0.5)
    police_siren.play()
    background_small = pygame.transform.scale(
        loader.IMAGES["outer-space.png"], (engine.scene_3d.imw, engine.scene_3d.imh)
    )
    background = pygame.transform.scale_by(background_small, PIXEL_SIZE)

    engine.set_background(background)
    # engine.scene_3d.add_obj(frame)
    engine.reset_wait_time()
    engine.until(
        2000, helpers.translate_object(enemy_ship, renderer.vec3.Vec3(0, 0, 10))
    )
    engine.wait(750)
    engine.until(
        2000, helpers.translate_object(enemy_ship, renderer.vec3.Vec3(-1, 2, 0))
    )
    engine.until(2000, helpers.rotate_object(enemy_ship, renderer.vec3.Vec3(0, 90, 0)))
    engine.wait(2000)
    engine.until(
        4000,
        helpers.fadein_text(
            "SURVIVE!", runfont, 0.1, (255, 255, 0), helpers.get_center(engine.screen)
        ),
    )
    engine.until(1000, helpers.rotate_object(enemy_ship, renderer.vec3.Vec3(15, 0, 0)))
    engine.wait(1500)
    engine.until(
        3000, helpers.translate_object(enemy_ship, renderer.vec3.Vec3(0, 0, -6))
    )
    engine.wait(2700)
    engine.until(
        2500, helpers.translate_object(enemy_ship, renderer.vec3.Vec3(0, 0, 3))
    )
    engine.after(3000, lambda engine: play_segment("main_game", engine))

    engine.scene_3d.add_obj(enemy_ship)
    engine.update()


@add_segment("main_game")
def _segment_main_game(engine):
    engine.reset_wait_time()
    enemy_ship = loader.MODELS["enemy_ship"]
    asteroid = loader.MODELS["rock"]
    loader.SOUNDS["police-siren.mp3"].fadeout(5000)
    asteroid.translate(renderer.vec3.Vec3(-10, 0, 0))
    assert (
        enemy_ship in engine.scene_3d.objects
    ), "main_game segment run before main_game_intro"
    #engine.scene_3d.objects.remove(enemy_ship)
    crosshair = sprites.Crosshair(engine.screen, engine.scene_clamp)
    engine.sprite_group.add(crosshair)
    def _click_handler(event):
        screen_pos = (
            (event.pos[0] - engine.scene_offset[0]) / PIXEL_SIZE,
            (event.pos[1] - engine.scene_offset[1]) / PIXEL_SIZE,
        )
        position = helpers.to_world_space(screen_pos, enemy_ship._projection_x_viewport)
        print("POSITION", position, "E", screen_pos)

    def _ship_loop_move(ship):
        print("MOVE")
        engine.until(
            300,
            helpers.translate_object(
                ship,
                renderer.vec3.Vec3(
                    random.randrange(-10, 11) / 10,
                    random.randrange(-10, 11) / 10,
                    random.randrange(-10, 11) / 10,
                ),
                clamp_top=-2,
                clamp_bottom=8,
                clamp_left=-7,
                clamp_right=3,
                clamp_front=-10,
            ),
        )
        print(ship.calculate_centerpoint())
        engine.after(300, lambda engine: _ship_loop_move(ship))

    def _asteroids_loop():
        a = asteroid.clone()
        a.translate(
            renderer.vec3.Vec3(
                random.randrange(-10, 11) / 10,
                random.randrange(-10, 11) / 10,
                random.randrange(-10, 11) / 10,
            )
        )
        if random.randrange(2):
            a.translate(renderer.vec3.Vec3(20, 0, 0))
        engine.until(
            5000,
            helpers.translate_object(
                a, renderer.vec3.Vec3(0, 0, random.randrange(18, 36))
            ),
        )
        engine.until(
            5000,
            helpers.rotate_object(
                a,
                renderer.vec3.Vec3(
                    random.randrange(360), random.randrange(360), random.randrange(360)
                ),
            ),
        )
        engine.after(5000, lambda engine: engine.scene_3d.objects.remove(a))
        engine.after(5000, lambda engine: a.cleanup())
        engine.scene_3d.add_obj(a)
        engine.update()

        engine.after(random.randrange(500, 2000), lambda engine: _asteroids_loop())

    _asteroids_loop()
    _ship_loop_move(enemy_ship)
    engine.add_event_handler(pygame.MOUSEBUTTONDOWN, _click_handler)
    engine.add_event_handler(pygame.MOUSEMOTION, crosshair.mousemotion_handler)

def play_segment(segment_name, engine):
    SEGMENTS[segment_name](engine)

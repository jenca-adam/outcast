import time
import pygame
import pygame_gui

from . import renderer
from . import loader
from . import helpers
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
    announcement = loader.SOUNDS["announcement.wav"]
    music = loader.SOUNDS["theme_violin.mp3"]
    titlefont = loader.FONTS[("airstrikeacad.ttf", 96)]
    engine.scene_3d.add_obj(horn)
    announcement.play()
    engine.wait(500)
    engine.until(21500, helpers.rotate_object(horn, renderer.vec3.Vec3(0, 167.441, 0)))
    engine.until(2000, helpers.translate_object(horn, renderer.vec3.Vec3(0, 0, -1)))
    engine.wait(20000)
    engine.after(0, lambda engine: music.play())
    engine.until(8000, helpers.translate_object(horn, renderer.vec3.Vec3(0, 0, -0.09)))
    engine.wait(6000)

    engine.until(
        4000,
        helpers.fadein_text(
            "CAST AWAY",
            titlefont,
            2.5,
            (0, 128, 128),
            helpers.get_center(engine.scene_3d.screen),
        ),
    )
    # engine.after(0, lambda engine:music.fadeout(4000))
    engine.wait(4000)  # block until the end
    engine.after(0, lambda engine: play_segment("destination_select", engine))

@add_segment("destination_select")
def _segment_destination_select(engine):
    def destination_select_button_handler(event):
        if event.type==pygame_gui.UI_BUTTON_PRESSED and event.ui_object_id in ("kepler", "gliese", "proxima"):
            engine["target"]=event.ui_object_id
            engine.remove_ui_event_handler("dest_butt")
            kepler_button.kill()
            gliese_button.kill()
            proxima_button.kill()
            label.kill()
            loader.SOUNDS["theme_violin.mp3"].fadeout(2000)
    engine.scene_3d.objects = []
    label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0,-500),(-1,-1)), text="Select a destination to flee to:", anchors={"center":"center"}, manager=engine.uimgr, object_id="select_label")
    kepler_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((-250,0), (-1, 50)),

                                             text='KEPLER 1649C',
                                             anchors={"center":"center"},
                                             manager=engine.uimgr,
                                             object_id="kepler")
    gliese_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((-25,0), (-1, 50)),

                                             text='GLIESE 6677CC',
                                             anchors={"center":"center"},
                                             manager=engine.uimgr,
                                             object_id="gliese")

    proxima_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((250,0), (-1, 50)),

                                             text='PROXIMA CENTAURI B',
                                             anchors={"center":"center"},
                                             manager=engine.uimgr,
                                             object_id="proxima")
    engine.add_ui_event_handler(destination_select_button_handler, "dest_butt")

def play_segment(segment_name, engine):
    SEGMENTS[segment_name](engine)

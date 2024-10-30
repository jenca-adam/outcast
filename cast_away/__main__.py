import pygame
import traceback
import os
try:
    import coloredlogs

    coloredlogs.install()
except:
    pass
from .msgbox import show_error
try:
    from . import loader
    from . import segment
    from . import engine
    from .scene import setup_scene
    from .settings import *
    from .mixer import init_mixer
    pygame.display.init()
    pygame.font.init()
    pygame.freetype.init()

    init_mixer()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    loader.load_all(screen)
    scene, image_offset = setup_scene(screen, PIXEL_SIZE)
# run_intro(screen)
    cast_away = engine.Engine(scene, screen, image_offset, TARGET_FPS)
#segment.play_segment("intro", cast_away)

    segment.play_segment("main_game_intro", cast_away)
    cast_away.loop()
except:
    pygame.display.quit()
    show_error(traceback.format_exc())

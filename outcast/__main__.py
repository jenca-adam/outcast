import pygame
import traceback
try:
    import coloredlogs

    coloredlogs.install()
except:
    pass
from .msgbox import show_error
from .settings import *

import tracemalloc 
  
#tracemalloc.start() 
def main():
    try:
        from . import loader
        from . import segment
        from . import engine
        from .scene import setup_scene
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
        outcast = engine.Engine(scene, screen, image_offset, TARGET_FPS)
        segment.play_segment(INITIAL_SEGMENT_NAME, outcast)
        # segment.play_segment("main_game_intro", outcast)
        outcast.loop()
    except Exception as e:

        if isinstance(e, SystemExit) or isinstance(e, KeyboardInterrupt):
            return
        pygame.mixer.quit()
        pygame.display.quit()
        pygame.quit()
        show_error(traceback.format_exc())


if __name__ == "__main__":
    main()

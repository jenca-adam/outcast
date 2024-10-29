import pygame

try:
    import coloredlogs

    coloredlogs.install()
except:
    pass
from . import loader
from . import segment
from .import engine
from .scene import setup_scene

PIXEL_SIZE = 10
pygame.display.init()
pygame.font.init()
pygame.freetype.init()
print("MIXER")
pygame.mixer.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
loader.load_all(screen)
scene = setup_scene(screen, PIXEL_SIZE)
# run_intro(screen)
cast_away = engine.Engine(scene)
segment.play_segment("intro", cast_away)
segment.play_segment("destination_select", cast_away)
cast_away.loop()

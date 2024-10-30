from .renderer import Scene
import pygame
from .settings import BACKFACE_CULLING, CAM_Z


def setup_scene(screen, pixel_size):
    ssize = screen.get_size()
    screen_square_size, screen_full_size = min(ssize), max(ssize)

    image_size = screen_square_size // pixel_size
    image_offset = screen_full_size // 2 - screen_square_size // 2
    surface = pygame.surface.Surface((screen_square_size, screen_square_size))
    scene = Scene()
    scene.set_kwargs(backface_culling=BACKFACE_CULLING)
    scene.set_defaults(cam_z=CAM_Z)
    scene.set_render_image(
        image_size,
        image_size,
        screen=surface,
        chunk_size=pixel_size,
        offset=(0, 0),
    )
    return scene, (image_offset, 0)

from .renderer import Scene
import pygame
from .settings import (
    BACKFACE_CULLING,
    CAM_Z,
    PHONG_DIFFUSE_COEFF,
    PHONG_AMBIENT_COEFF,
    PHONG_SPECULAR_COEFF,
    LIGHTING
)


def setup_scene(screen, pixel_size):
    ssize = screen.get_size()
    screen_square_size, screen_full_size = min(ssize), max(ssize)

    image_size = screen_square_size // pixel_size
    image_offset = screen_full_size // 2 - screen_square_size // 2
    surface = pygame.surface.Surface((screen_square_size, screen_square_size))
    scene = Scene()
    scene.set_kwargs(
        backface_culling=BACKFACE_CULLING,
        diffuse_coeff=PHONG_DIFFUSE_COEFF,
        specular_coeff=PHONG_SPECULAR_COEFF,
        ambient_coeff=PHONG_AMBIENT_COEFF,
        lighting=LIGHTING
    )
    scene.set_defaults(cam_z=CAM_Z)
    scene.set_render_image(
        image_size,
        image_size,
        screen=surface,
        chunk_size=pixel_size,
        offset=(0, 0),
    )
    return scene, (image_offset, 0)

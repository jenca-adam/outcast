from .renderer import Scene


def setup_scene(screen, pixel_size):
    ssize = screen.get_size()
    screen_square_size, screen_full_size = min(ssize), max(ssize)

    image_size = screen_square_size // pixel_size
    image_offset = screen_full_size // 2 - screen_square_size // 2

    scene = Scene()
    scene.set_render_image(
        image_size,
        image_size,
        screen=screen,
        chunk_size=pixel_size,
        offset=(image_offset, 0),
    )
    return scene

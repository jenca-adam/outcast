from .renderer import Vec3, Matrix


def get_center(sc):
    sz = sc.get_size()
    return (sz[0] // 2, sz[1] // 2)


def rotate_object(obj, speed):
    def ro_inner(engine):
        obj.rotate(speed * engine.delta)
        engine.update()

    return ro_inner


def translate_object(
    obj,
    speed,
    clamp_top=None,
    clamp_bottom=None,
    clamp_left=None,
    clamp_right=None,
    clamp_front=None,
    clamp_back=None,
):
    def to_inner(engine):
        obj.translate(speed * engine.delta)
        if clamp_top is not None and obj.translation.y < clamp_top:
            obj.translate(Vec3(clamp_top - obj.translation.y))
        elif clamp_bottom is not None and obj.translation.y > clamp_bottom:
            obj.translate(Vec3(clamp_bottom - obj.translation.y))
        if clamp_left is not None and obj.translation.x < clamp_left:
            obj.translate(Vec3(clamp_left - obj.translation.x))
        elif clamp_right is not None and obj.translation.x > clamp_right:
            obj.translate(Vec3(clamp_right - obj.translation.x))
        if clamp_front is not None and obj.translation.z < clamp_front:
            obj.translate(Vec3(clamp_front - obj.translation.z))
        elif clamp_back is not None and obj.translation.z > clamp_back:
            obj.translate(Vec3(clamp_back - obj.translation.z))
        engine.update()

    return to_inner


def render_to_center(font, sc, cp, text, color, draw_over=False, engine=None):
    rect = font.get_rect(text)

    def rtc_inner():
        font.render_to(
            sc, (cp[0] - rect.width // 2, cp[1] - rect.height // 2), text, color
        )

    if not draw_over:
        rtc_inner()
    else:
        engine.topcall(rtc_inner)


def fadein_text(text, font, time, color, cp):
    rep = 0

    def fit_inner(engine):
        nonlocal rep  # wtf i've never heard of this
        render_to_center(
            font,
            engine.screen,
            cp,
            text,
            color + (min(255, rep * 255 / time),),
            draw_over=True,
            engine=engine,
        )
        rep += engine.delta

    return fit_inner


def to_world_space(click_pos, matrix):
    im = matrix.inverse4x4()
    v3 = Vec3(*click_pos, 0)
    o=Vec3.from_matrix3(im @ Matrix.from_vector(v3))
    o.z=-o.z
    return o

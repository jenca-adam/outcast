def get_center(sc):
    sz = sc.get_size()
    return (sz[0] // 2, sz[1] // 2)


def rotate_object(obj, speed):
    def ro_inner(engine):
        obj.rotate(speed * engine.delta)
        engine.update()
    return ro_inner


def translate_object(obj, speed):
    def to_inner(engine):
        obj.translate(speed * engine.delta)
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
            engine.scene_3d.screen,
            cp,
            text,
            color + (min(255, rep * 255 / time),),
            draw_over=True,
            engine=engine,
        )
        rep += engine.delta

    return fit_inner

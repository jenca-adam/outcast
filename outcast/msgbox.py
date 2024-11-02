import pygame_gui
import pygame
import os
from . import loader
import sys


def show_error(errtext="An error has occurred", errtitle="ERROR", size=(600, 400)):
    pygame.font.init()
    print(errtext, file=sys.stderr)
    try:
        # CREATE A NEW SCREEN UI MANAGER IN CASE THE DEFAULT ONE CRASHED
        ww, wh = size
        screen = pygame.display.set_mode((ww, wh), pygame.NOFRAME)
        uimgr = pygame_gui.UIManager(
            (ww + 100, wh + 100), loader.FILES / "theme/error.json"
        )
        popup = pygame_gui.windows.UIMessageWindow(
            (0, 0, ww, wh),
            errtext.replace("<", "&lt;").replace(">", "&gt;"),
            uimgr,
            window_title=errtitle,
        )
        clock = pygame.time.Clock()

        while True:
            delta = clock.tick(60) / 1000
            for event in pygame.event.get():
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    os._exit(0)
                uimgr.process_events(event)
            screen.fill((0, 0, 0))
            uimgr.draw_ui(screen)
            uimgr.update(delta)
            pygame.display.flip()
    except:
        print("FATAL: errbox show failed", file=sys.stderr)
        raise

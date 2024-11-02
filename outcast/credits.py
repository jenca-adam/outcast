import pygame_gui
from . import loader
def show_credits(engine):
    credits_window = pygame_gui.windows.UIMessageWindow((engine.screen.get_size()[0]//2-300,engine.screen.get_size()[1]//2-300,600,600), loader.TEXTS["credits.html"], manager=engine.uimgr, object_id="#credits_window", window_title="Credits")

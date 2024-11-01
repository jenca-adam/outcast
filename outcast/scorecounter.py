import pygame_gui
import pygame
from pygame_gui.core import ObjectID
from . import loader
from .engine import TIMER, TIMEOUT
from .settings import DIFFICULTIES


class ScoreCounter:
    def __init__(self, engine):
        self.engine = engine
        self.score = 0
        engine["score"] = self.score
        self.label = pygame_gui.elements.UILabel(
            pygame.rect.Rect(0, 10, -1, -1),
            text=f"SCORE: {self.score}",
            manager=engine.uimgr,
            anchors={"centerx": "centerx", "top": "top"},
            object_id=ObjectID(object_id="#score_label_big", class_id="@pixelated"),
        )

    def show_score_on_screen(self, text, pos, clsid="@pixelated_big"):
        sadd_label = pygame_gui.elements.UILabel(
            pygame.rect.Rect(*pos, -1, -1),
            text=text,
            manager=self.engine.uimgr,
            object_id=clsid,
        )
        sadd_label.set_active_effect(pygame_gui.TEXT_EFFECT_FADE_OUT)

        def move_label(engine):
            sadd_label.rect = sadd_label.rect.move((0, -1))

        self.engine.after(1000, lambda engine: sadd_label.kill(), use_offset=False)

        self.engine.until(1000, move_label)

    def update_score(self, sd, position=None, clsid="@pixelated_big"):

        self.score += sd
        self.engine["score"] = self.score
        if position is not None:
            self.show_score_on_screen(f"+{sd}", position, clsid)
        self.label.set_text(f"SCORE: {self.score}")

    def kill(self):
        self.label.kill()


class TimeCounter:
    def __init__(self, engine):
        self.engine = engine
        self.time = 0
        self.timeout = DIFFICULTIES[engine["target"]]["timeout"]
        engine["time"] = self.time
        self.label = pygame_gui.elements.UILabel(
            pygame.rect.Rect(0, 50, -1, -1),
            text=f"TIME: {self.time}",
            manager=engine.uimgr,
            anchors={"centerx": "centerx", "top": "top"},
            object_id=ObjectID(object_id="#score_label_big", class_id="@pixelated"),
        )

        engine.add_event_handler(TIMER, self.update)

    def update(self, *_):

        self.time += 1
        if self.time == self.timeout:
            pygame.event.post(pygame.event.Event(TIMEOUT))
        self.engine["time"] = self.time
        self.label.set_text(f"TIME: {self.time}")

    def kill(self):
        self.label.kill()

import pygame
import time
import random
import os
import traceback
import pygame_gui
from . import loader


class AfterSequence:
    def __init__(self, engine, time):
        self.engine = engine
        self.time = time

    def after(self, t, func):
        return self.engine.after(self.time + t, func)

    def until(self, t, func):
        return self.engine.until(self.time, func, delay=t)


class Engine:
    def __init__(self, scene_3d, fps=30):
        self.scene_3d = scene_3d
        self._event_handlers = {}
        self._key_handlers = {}
        self._afters = []
        self._untils = []
        self._topcalls = set()
        self._uihandlers = {}
        self.fps = fps
        self._exit_flag = False
        self._update_flag = False
        self.delta = 0
        self.data ={}
        self.total_time_offset = 0
        self.clock = pygame.time.Clock()
        self.uimgr = pygame_gui.UIManager(
            self.scene_3d.screen.get_size(), theme_path=loader.FILES / "theme/theme.json"
        )
    def wait(self, ms):
        self.total_time_offset += ms

    def quit(self):
        self._exit_flag = True
    def update(self):
        self._update_flag=True
    def _handle_events(self):
        for key in self._key_handlers:
            if pygame.key.get_pressed()[key]:
                self._key_handlers[key]()
        for event in pygame.event.get():
            print(event)
            if event.type in self._event_handlers:
                self._event_handlers[event.type](event)
            if event.type == pygame.QUIT:
                self.quit()
            if pygame.USEREVENT<=event.type <= pygame.NUMEVENTS:
                for uih in list(self._uihandlers.values()):
                    uih(event)
            self.uimgr.process_events(event)
    def add_ui_event_handler(self,handler, handler_id):
        self._uihandlers[handler_id]=handler
    def remove_ui_event_handler(self, handler_id):
        del self._uihandlers[handler_id]
    def _handle_afters(self):
        for i, (timeout, timer) in enumerate(self._afters):
            if time.perf_counter() >= timeout:
                timer(self)
                del self._afters[i]

    def _handle_untils(self):
        for i, (timeout, timer) in enumerate(self._untils):
            if time.perf_counter() < timeout:
                timer(self)
            else:
                del self._untils[i]

    def _handle_topcalls(self):
        for tc in self._topcalls:
            tc()
        self._topcalls = set()

    def loop(self):
        try:
            while not self._exit_flag:
                self.delta = self.clock.tick(self.fps) / 1000
                self.uimgr.update(self.delta)
                self.scene_3d.screen.fill((0, 0, 0))
                self._handle_events()
                self._handle_afters()
                self._handle_untils()
                if self._update_flag:
                    print("UPDATE")
                    self.scene_3d.render()
                self._update_flag=False
                self.uimgr.draw_ui(self.scene_3d.screen)
                self._handle_topcalls()
                pygame.display.flip()
        finally:
            print(traceback.format_exc())
            pygame.display.quit()
            os._exit(0)

    def after(self, t, func, seq=True, delay=0, use_offset=True):
        self._afters.append(
            (
                (t + delay + self.total_time_offset * use_offset) / 1000
                + time.perf_counter(),
                func,
            )
        )
        return AfterSequence(self, t * seq + delay)

    def until(self, t, func, seq=True, delay=0, use_offset=True):
        if delay or (self.total_time_offset and use_offset):
            self.after(
                delay + self.total_time_offset,
                lambda self: self.until(t, func, seq, delay=0, use_offset=False),
                use_offset=False,
            )
        else:
            self._untils.append(((t) / 1000 + time.perf_counter(), func))
        return AfterSequence(self, t * seq + delay)

    def topcall(self, func):
        self._topcalls.add(func)

    def __getitem__(self, it):
        return self.data[it]
    def __setitem__(self, it, val):
        self.data[it]=val

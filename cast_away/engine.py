import pygame
import time
import pygame_gui
from . import loader
from .fonts import HELVETICA_XSMALL

FRAME = 0xF000


class AfterSequence:
    def __init__(self, engine, time):
        self.engine = engine
        self.time = time

    def after(self, t, func):
        return self.engine.after(self.time + t, func)

    def until(self, t, func):
        return self.engine.until(self.time, func, delay=t)


class Engine:
    def __init__(self, scene_3d, screen, scene_offset, fps=60):
        self.scene_3d = scene_3d
        self.scene_offset = scene_offset
        self.screen = screen
        self.scene_clamp = pygame.rect.Rect(*scene_offset, *scene_3d.screen.size)
        self._event_handlers = {}
        self._key_handlers = {}
        self._afters = []
        self._untils = []
        self._topcalls = set()
        self._uihandlers = {}
        self.fps = fps
        self.frame_counter = 0
        self._background = None
        self._exit_flag = False
        self._update_flag = False
        self.delta = 0
        self.data = {}
        self.total_time_offset = 0
        self.clock = pygame.time.Clock()
        self.uimgr = pygame_gui.UIManager(
            self.screen.get_size(),
            theme_path=loader.FILES / "theme/theme.json",
        )
        self.sprite_group = pygame.sprite.Group()

    def wait(self, ms):
        self.total_time_offset += ms

    def set_background(self, surf):
        self._background = surf

    def reset_background(self):
        self._background = (0, 0, 0)

    def quit(self):
        self._exit_flag = True

    def update(self):
        self._update_flag = True

    def add_event_handler(self, event, handler):
        if event not in self._event_handlers:
            self._event_handlers[event] = set()
        self._event_handlers[event].add(handler)

    def _handle_events(self):
        for key in self._key_handlers:
            if pygame.key.get_pressed()[key]:
                self._key_handlers[key]()
        for event in pygame.event.get():
            if event.type in self._event_handlers:
                for eh in self._event_handlers[event.type]:
                    eh(event)
            if event.type == pygame.QUIT:
                self.quit()
            if pygame.USEREVENT <= event.type <= pygame.NUMEVENTS:
                for uih in list(self._uihandlers.values()):
                    uih(event)
            self.uimgr.process_events(event)
        self._emit_frame_event()

    def _emit_frame_event(self):
        fr_event = pygame.event.Event(
            FRAME,
            {"frame_counter": self.frame_counter, "delta": self.delta, "engine": self},
        )
        for eh in self._event_handlers.get(FRAME, set()):
            eh(fr_event)

    def add_ui_event_handler(self, handler, handler_id):
        self._uihandlers[handler_id] = handler

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
            # previous_frame_start=pygame.time.get_ticks()
            while not self._exit_flag:
                self.frame_counter += 1
                # current_frame_start = pygame.time.get_ticks()
                self.delta = self.clock.tick(self.fps) / 1000
                # self.delta = (current_frame_start - previous_frame_start)/1000
                # previous_frame_start = current_frame_start
                self.uimgr.update(self.delta)
                self.screen.fill((0, 0, 0))
                self._handle_events()
                self._handle_afters()
                self._handle_untils()
                if self._update_flag:
                    if self._background:
                        self.scene_3d.screen.blit(self._background, (0, 0))
                    else:
                        self.scene_3d.screen.fill((0, 0, 0))
                    self.scene_3d.render()
                    self._update_flag = False
                self.screen.blit(self.scene_3d.screen, self.scene_offset)
                self.sprite_group.draw(self.screen)
                self.uimgr.draw_ui(self.screen)
                self._handle_topcalls()
                if self.delta:
                    self.screen.blit(
                        HELVETICA_XSMALL.render(
                            f"{1/self.delta:.2f} FPS", True, (255, 255, 255)
                        )
                    )
                # delay = 1/self.fps - (pygame.time.get_ticks()-current_frame_start)
                pygame.display.flip()

                # pygame.time.delay(int(delay//1000))
        finally:
            pygame.display.quit()

    def after(self, t, func, seq=True, delay=0, use_offset=True):
        self._afters.append(
            (
                (t + delay + self.total_time_offset * use_offset) / 1000
                + time.perf_counter(),
                func,
            )
        )
        return AfterSequence(self, t * seq + delay)

    def reset_wait_time(self):
        self.total_time_offset = 0

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
        self.data[it] = val

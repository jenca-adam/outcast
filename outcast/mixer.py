import pygame.mixer
import threading
import time
from . import msgbox
from .settings import MIXER_WAIT_TIME
from .helpers import get_dict


class Channel:
    def __init__(self, name, pyg_channel=None):
        self.name = name
        self.channel = pyg_channel

    def set_channel(self, pyg_channel):
        self.channel = pyg_channel
        self.__dict__.update(get_dict(self.channel))
    def fadeout_current(self, *args):
        try:
            self.get_sound().fadeout(*args)
        except:
            pass
    def __getattr__(self, attr):
        if hasattr(pygame.mixer.Channel, attr):
            if self.channel is None:
                if callable(getattr(pygame.mixer.Channel, attr)):
                    raise RuntimeError(
                        f"{self.name}: can't call {attr}(): not initialized"
                    )
                else:
                    raise RuntimeError(
                        f"{self.name}: can't get {attr}: not initialized"
                    )
            return getattr(self.channel, attr)
        raise AttributeError(attr)


MUSIC_CHANNEL = Channel("music")
SFX_CHANNEL = Channel("sfx")


def init_mixer():
    stop_event = threading.Event()

    def mixer_init_task():
        pygame.mixer.init()
        stop_event.set()

    t = threading.Thread(target=mixer_init_task)
    t.start()
    start = time.perf_counter()
    while time.perf_counter() - start < MIXER_WAIT_TIME:
        if stop_event.is_set():
            print("Mixer Init OK")
            break
        print(
            f"\rWaiting for mixer init ({MIXER_WAIT_TIME-time.perf_counter()+start:.2f}s left)...",
            end="",
        )
    else:
        msgbox.show_error(
            f"pygame.mixer.init() took too long ({MIXER_WAIT_TIME}s). Check your audio configuration/any apps using the audio output.",
            "MIXER ERROR",
            (400, 200),
        )
    MUSIC_CHANNEL.set_channel(pygame.mixer.Channel(0))
    SFX_CHANNEL.set_channel(pygame.mixer.Channel(1))

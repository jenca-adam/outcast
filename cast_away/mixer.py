import pygame.mixer
import threading
import time
from . import msgbox
from .settings import MIXER_WAIT_TIME


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

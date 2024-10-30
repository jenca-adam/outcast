import pygame.mixer
import threading
import time
import os
import sys
from . import msgbox
from .settings import MIXER_WAIT_TIME


def init_mixer():
    stop_event = threading.Event()

    def timer_task(secs):
        start = time.perf_counter()
        while time.perf_counter() - start < secs:
            if stop_event.is_set():
                break
            print(
                f"Waiting for mixer init ({secs-time.perf_counter()+start:.2f}s left)...",
                end="\r",
            )
        else:
            msgbox.show_error(
                f"pygame.mixer.init() took too long ({secs}s). Check your audio configuration/any apps using the audio output.",
                "MIXER ERROR",
                (400,200),
            )
            os._exit(1)  # Kill all threads

    t = threading.Thread(
        target=timer_task, args=(MIXER_WAIT_TIME,), daemon=False
    ).start()
    pygame.mixer.init()
    stop_event.set()

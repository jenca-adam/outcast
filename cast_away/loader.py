import os
from .renderer import ObjFile
import logging
import tqdm
from .pygutils import ProgressBar
import pygame.mixer
import pygame.freetype
import itertools
import pathlib
from . import settings
MODELS = {}
SOUNDS = {}
FONTS = {}
FILES = pathlib.Path(os.path.dirname(__file__)) / "files"


def load_obj(obj_name):
    objdir = FILES/"obj"/obj_name
    objfile = objdir/f"{obj_name}.obj"
    if not os.path.exists(objfile):
        raise FileNotFoundError(f"model not found: {obj_name}")
    obj = ObjFile.open(objfile)
    for texture in ("diffuse", "nm_tangent", "spec"):
        texture_fn = objdir/f"{obj_name}_{texture}.ppm"
        if not os.path.exists(texture_fn):
            logging.warn(f"texture {texture} for {obj_name} not found")
            continue
        obj.add_texture(texture, str(texture_fn))
    return obj


def load_all(screen):
    objs, audios, fonts = map(
        os.listdir, map(FILES.__truediv__, ("obj", "audio", "fonts"))
    )
    pbar = ProgressBar(
        screen,
        len(objs) + len(audios) + len(fonts) * len(settings.FONT_SIZES),
    )
    for obj_name in pbar.partial_iter(objs):
        MODELS[obj_name] = load_obj(obj_name)
    for audio_name in pbar.partial_iter(audios):
        SOUNDS[audio_name] = pygame.mixer.Sound(FILES / "audio" / audio_name)
    for font_name, font_size in pbar.partial_iter(
        itertools.product(fonts, settings.FONT_SIZES)
    ):
        FONTS[(font_name, font_size)] = pygame.freetype.Font(
            FILES / "fonts" / font_name, font_size
        )

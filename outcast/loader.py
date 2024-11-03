import os
from .renderer import ObjFile, Vec3
import logging
from .pygutils import ProgressBar
import pygame.mixer
import pygame.freetype
import pygame.image
import itertools
import pathlib
from . import settings
import json

MODELS = {}
SOUNDS = {}
FONTS = {}
IMAGES = {}
TEXTS = {}
FILES = pathlib.Path(os.path.dirname(__file__)) / "../files"
with open(FILES / "objects_info.json", "r") as f:
    OBJ_INFO = json.load(f)


def load_obj(obj_name):
    objdir = FILES / "obj" / obj_name
    objfile = objdir / f"{obj_name}.obj"
    if not os.path.exists(objfile):
        raise FileNotFoundError(f"model not found: {obj_name}")
    scale = OBJ_INFO.get(obj_name, {}).get("scale", 1)
    obj = ObjFile.open(objfile, scale=scale)
    for texture in ("diffuse", "nm_tangent", "spec"):
        texture_fn = objdir / f"{obj_name}_{texture}.ppm"
        if not os.path.exists(texture_fn):
            logging.warn(f"texture {texture} for {obj_name} not found")
            if texture == "diffuse":
                raise LookupError(f"missing diffuse texture for {obj_name}")
            continue
        obj.add_texture(texture, str(texture_fn))
    return apply_oi_transforms(obj_name, obj)


def apply_oi_transforms(obj_name, obj):
    rotation = OBJ_INFO.get(obj_name, {}).get("rotate", None)
    if rotation is not None:
        obj.rotate(Vec3(*rotation))
    translation = OBJ_INFO.get(obj_name, {}).get("translate", None)
    if translation is not None:
        obj.translate(Vec3(*translation))
    return obj


def load_all(screen):
    objs, audios, fonts, images, txts = map(
        os.listdir, map(FILES.__truediv__, ("obj", "audio", "fonts", "images", "text"))
    )
    pbar = ProgressBar(
        screen,
        len(objs) + len(audios) + len(fonts) * len(settings.FONT_SIZES) + len(images),
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
    for image_name in pbar.partial_iter(images):
        IMAGES[image_name] = pygame.image.load(FILES / "images" / image_name)
    for text_name in pbar.partial_iter(txts):
        with open(FILES / "text" / text_name, "r", encoding="utf-8") as f:
            TEXTS[text_name] = f.read()

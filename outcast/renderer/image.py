from .ppm import export_image, read_image
from . import cCore
import enum
import pygame


class ImageBackend(enum.Enum):
    PPM = 0
    PGM = 1


def mkhex(color):
    return "#" + "".join(f"{int(p):02x}" for p in color)


class Image:
    def __init__(
        self, arr, backend=ImageBackend.PPM, screen=None, chunk_size=1, offset=0
    ):
        self.arr = arr
        self.backend = backend
        self.width = len(arr[0])
        self.height = len(arr)
        self.x_offset, self.y_offset = offset
        if self.backend == ImageBackend.PGM:
            self._screen = screen
            self.chunk_size = chunk_size
            # self._pgm_draw()

    def _pgm_draw(self):
        for x, row in enumerate(self.arr):
            for y, color in enumerate(row):
                self._pgm_putpixel(x, y, color)

    def _pgm_putpixel(self,col,coords):
        x,y=coords
        if self._screen is None:
            raise TypeError("can't _pgm_putpixel(): no screen")
        pygame.draw.rect(
            self._screen,
            tuple(max(0, int(i)) for i in col),
            (
                x * self.chunk_size + self.x_offset,
                y * self.chunk_size + self.y_offset,
                self.chunk_size,
                self.chunk_size,
            ),
        )

    @classmethod
    def new(cls, x, y, backend=ImageBackend.PPM, **kwargs):
        return cls([[(0, 0, 0) for _ in range(x)] for _ in range(y)], backend, **kwargs)

    @classmethod
    def from_ppm(cls, fn):
        return cls(read_image(fn))

    def save(self, filename):
        with open(filename, "wb") as f:
            f.write(export_image(self.arr))

    def uv(self, coords):
        try:
            return vec3.Vec3(
                *self[
                    abs(coords.x * (self.width - 1)), -abs(coords.y * (self.height - 1))
                ]
            )
        except:
            return vec3.Vec3(255, 0, 0)

    def __getitem__(self, coords):
        x, y = map(int, coords)
        return self.arr[y][x]

    def __setitem__(self, coords, pix):
        # x, y = map(int, coords)
        x, y = coords
        # print(x,y,pix)
        if self.backend == ImageBackend.PGM:
            self._pgm_putpixel(x, y, pix)
        else:
            try:
                self.arr[y][x] = pix
            except:
                pass

    def draw_line(self, start, end, color):
        x0, y0, *_ = map(int, start)
        x1, y1, *_ = map(int, end)
        transposed = False
        if abs(x0 - x1) < abs(y0 - y1):
            x0, y0, x1, y1 = y0, x0, y1, x1
            transposed = True
        if x0 > x1:
            x0, x1, y0, y1 = x1, x0, y1, y0
        dx, dy = x1 - x0, y1 - y0
        derror2 = abs(dy) * 2
        error2 = 0
        y = y0
        for x in range(x0, x1):
            if transposed:
                self[y, x] = color
            else:
                self[x, y] = color
            error2 += derror2
            if error2 > dx:
                y += (-1) ** (y0 >= y1)
                error2 -= dx * 2

    def draw_triangle(self, v0, v1, v2, color_or_texture, *args, **kwargs):

        cCore.draw_triangle(
            self._pgm_putpixel, self.width, self.height, v0, v1, v2, color_or_texture, *args, **kwargs
        )
        """minx = max(0, min(v0.x, v1.x, v2.x))
        miny = max(0, min(v0.y, v1.y, v2.y))
        maxx = min(self.width, max(v0.x, v1.x, v2.x))
        maxy = min(self.height, max(v0.y, v1.y, v2.y))
        for x in range(int(minx), int(maxx + 1)):
            for y in range(int(miny), int(maxy + 1)):
                col = get_color(self,v0, v1, v2, x, y, color_or_texture, *args, **kwargs)
                if col is not None:
                    self[x,y]=col"""

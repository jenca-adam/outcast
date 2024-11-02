import sys
import math


def export_image(image_data):
    w, h = len(image_data[0]), len(image_data)
    header = f"P6\n{w} {h}\n255\n".encode("ascii")
    body = []
    for row in image_data:
        for col in row:
            body.append(bytes(map(int, col)))
    return header + b"".join(body)


def write_header(w, h):
    sys.stdout.buffer.write(f"P6\n{w} {h}\n255\n".encode("ascii"))


def read_image(ppm_file):
    img = []
    line = []
    with open(ppm_file, "rb") as f:
        mode = f.readline().strip()
        if mode != b"P6":
            raise NotImplementedError(f"unsupported mode: {mode}")
        w, h = map(int, f.readline().strip().split())
        maxn = int(f.readline().strip())
        nbytes = int(math.log(maxn + 1, 256))
        for pix in range(w * h):
            if nbytes == 1:
                line.append(tuple(f.read(3)))
            else:
                line.append(
                    tuple(
                        (255 * int.from_bytes(f.read(nbytes), "big")) // maxn
                        for _ in range(3)
                    )
                )
            if pix % w == w - 1:
                img.append(line)
                line = []
    return img


def write_color(r, g, b):
    sys.stdout.buffer.write(bytes((r, g, b)))



from . import image, vec3, cCore
import random
import tqdm
import math
import asyncio

LIGHT_DIR = vec3.Vec3(0, 0, -1)
CAM_Z = 3
NEAR_PLANE = -2.9


def background(f):
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, f, *args, **kwargs)

    return wrapped


class ObjFile:
    def __init__(self, vertices, texture_vertices, vertex_normals, faces, textures={}):
        self.vertices = vertices
        self.texture_vertices = texture_vertices
        self.vertex_normals = vertex_normals
        self.faces = faces
        self.centerpoint = self.calculate_centerpoint()
        self.light_dir = LIGHT_DIR
        self.textures = {}
        self.model_view = cCore.Matrix.identity(4)
        self.rotation = vec3.Vec3(0, 0, 0)
        self.translation = vec3.Vec3(0, 0, 0)
        self._cached_img = None
        self.cam_z = CAM_Z
        self._imw, self._imh = (None, None)
        for slot, file in textures.items():
            self.add_texture(slot, file)

    def look_at(self, eye, center, up):
        self.cam_z = eye.z
        self.model_view = cCore.Matrix.lookat(eye, center, up)

    def set_render_image(self, imw, imh, screen=None, chunk_size=1, offset=0):
        self._cached_img = image.Image.new(
            imw,
            imh,
            backend=image.ImageBackend.PGM if screen else image.ImageBackend.PPM,
            screen=screen,
            chunk_size=chunk_size,
            offset=offset,
        )
        self._imw, self._imh = imw, imh

    def add_texture(self, texture_type, texture_file):
        self.textures[texture_type] = cCore.Texture.from_ppm(texture_file)

    def calculate_centerpoint(self):

        vertex_sum = sum(self.vertices, vec3.Vec3(0, 0, 0))
        return vertex_sum / len(self.vertices)

    def translate(self, delta):
        self.translation += delta
        *self.vertices, self.centerpoint = [
            vert + delta for vert in (*self.vertices, self.centerpoint)
        ]

    def rotate(self, thetas, degrees=True):
        if degrees:
            thetas = vec3.array(math.radians(theta) for theta in thetas)
            self.rotation += thetas
        cp = self.centerpoint
        self.translate(-cp)
        self.apply(vec3.Matrix.rotx(thetas.x))
        self.apply(vec3.Matrix.roty(thetas.y))
        self.apply(vec3.Matrix.rotz(thetas.z))
        self.translate(cp)
        self.light_dir = vec3.Vec3.from_matrix3(
            vec3.Matrix.rotx(-thetas.x)
            @ vec3.Matrix.roty(-thetas.y)
            @ vec3.Matrix.rotz(-thetas.z)
            @ vec3.Matrix.from_vector(self.light_dir)
        )

    @property
    def rotation_matrix(self):
        return (
            vec3.Matrix.rotx(self.rotation.x)
            @ vec3.Matrix.roty(self.rotation.y)
            @ vec3.Matrix.rotz(self.rotation.z)
        )

    def apply(self, transform):
        *self.vertices, self.centerpoint = [
            vec3.Vec3.from_matrix3(transform @ vec3.Matrix.from_vector(vert))
            for vert in (*self.vertices, self.centerpoint)
        ]
        self.vertex_normals = [
            vec3.Vec3.from_matrix3(transform @ vec3.Matrix.from_vector(norm))
            for norm in self.vertex_normals
        ]

    def reset_transforms(self):
        self.rotate(-self.rotation, degrees=False)
        self.translate(-self.translation)
        self.light_dir = LIGHT_DIR

    def render_wireframe(self, imw, imh, color, outfile):
        img = image.Image.new(imw, imh)
        for face in self.faces:
            for i in range(3):
                v0, v1 = (
                    self.vertices[face[i][0] - 1],
                    self.vertices[face[(i + 1) % 3][0] - 1],
                )
                x0 = (v0.x + 1) * imw / 2
                x1 = (v1.x + 1) * imw / 2
                y0 = (v0.y + 1) * imh / 2
                y1 = (v1.y + 1) * imh / 2
                img.draw_line((x0, y0), (x1, y1), color)
        img.save(outfile)

    def render_triangles_normals(self, imw, imh, outfile):
        img = image.Image.new(imw, imh)
        zbuffer = {}
        for face in self.faces:
            screen_coords = [
                vec3.Vec3(
                    int((self.vertices[f[0] - 1].x + 1) * imw // 2),
                    int((self.vertices[f[0] - 1].y + 1) * imh // 2),
                    0,
                )
                for f in face
            ]
            world_coords = [self.vertices[f[0] - 1] for f in face]
            n = (
                (world_coords[2] - world_coords[0])
                .cross(world_coords[1] - world_coords[0])
                .normalized()
            )
            intensity = n.dot(LIGHT_DIR)
            if intensity > 0:
                img.draw_triangle(
                    *screen_coords, vec3.Vec3(255, 255, 255) * intensity, zbuffer
                )
        img.save(outfile)

    def render_triangles_texture(self, imw, imh, outfile):
        texture_img = self.textures.get("diffuse")
        if texture_img is None:
            raise LookupError(
                'diffuse texture not found. Use add_texture("diffuse", ...) to add it.\n'
                f"Loaded textures: {self.textures}"
            )
        img = image.Image.new(imw, imh)
        zbuffer = {}
        for face in tqdm.tqdm(self.faces):
            world_coords = [self.vertices[f[0] - 1] for f in face]
            n = (
                (world_coords[2] - world_coords[0])
                .cross(world_coords[1] - world_coords[0])
                .normalized()
            )
            if n.dot(LIGHT_DIRself.light_dir) <= 0:
                continue
            screen_coords = [
                vec3.Vec3(int((wc.x + 1) * imw / 2), int((wc.y + 1) * imh / 2), -wc.z)
                for wc in world_coords
            ]
            img.draw_triangle(
                *screen_coords,
                texture_img,
                zbuffer,
                texture_coords=tuple(self.texture_vertices[f[1] - 1] for f in face),
            )

        img.save(outfile)

    def render_triangles_gouraud_perspective(self, imw, imh, tint, outfile):
        img = image.Image.new(imw, imh)
        zbuffer = {}
        projection = vec3.Matrix.identity(4)
        viewport = vec3.Matrix.viewport(imw / 8, imh / 8, imw * 3 / 4, imh * 3 / 4)
        projection[3][2] = 1 / CAM_Z

        for face in tqdm.tqdm(self.faces):
            world_coords = [self.vertices[f[0] - 1] for f in face]
            screen_coords = [
                vec3.Vec3.from_matrix(
                    viewport @ projection @ vec3.Matrix.from_vector(wc)
                )
                for wc in world_coords
            ]
            n = (
                (world_coords[2] - world_coords[0])
                .cross(world_coords[1] - world_coords[0])
                .normalized()
            )
            if n.dot(LIGHT_DIR) <= 0:
                continue
            img.draw_triangle(
                *screen_coords,
                tint,
                zbuffer,
                vertex_normals=tuple(self.vertex_normals[f[2] - 1] for f in face),
            )
        img.save(outfile)

    def render(
        self,
        imw=None,
        imh=None,
        outfile=None,
        screen=None,
        lighting="phong",
        chunk_size=1,
        zbuffer=None,
        **kwargs,
    ):
        if zbuffer is None:
            zbuffer = {}
        normal_img = self.textures.get("normal")
        specular_img = self.textures.get("specular")
        if normal_img:
            kwargs["normal_map"] = normal_img
        if specular_img:
            kwargs["specular_map"] = specular_img
        texture_img = self.textures.get("diffuse")
        if texture_img is None:
            raise LookupError(
                'diffuse texture not found. Use add_texture("diffuse", ...) to add it.\n'
                f"Loaded textures: {self.textures}"
            )
        if (imw is None or imh is None) and self._cached_img is None:
            raise TypeError("Must provide imw and imh or call set_render_image")
        img = self._cached_img or image.Image.new(
            imw,
            imh,
            backend=image.ImageBackend.PGM if screen else image.ImageBackend.PPM,
            screen=screen,
            chunk_size=chunk_size,
        )
        imw, imh = img.width, img.height
        projection = vec3.Matrix.projection(CAM_Z)
        viewport = vec3.Matrix.viewport(imw / 8, imh / 8, imw * 3 / 4, imh * 3 / 4)

        def render_face(face):
            world_coords = tuple(self.vertices[f[0] - 1] for f in face)
            if any(coor.z < NEAR_PLANE for coor in world_coords):
                return
            screen_coords = tuple(viewport @ projection @ wc for wc in world_coords)
            n = (
                (world_coords[2] - world_coords[0])
                .cross(world_coords[1] - world_coords[0])
                .normalized()
            )
            if n.dot(LIGHT_DIR) <= 0:
                return
            img.draw_triangle(
                *screen_coords,
                texture_img,
                zbuffer,
                texture_coords=tuple(self.texture_vertices[f[1] - 1] for f in face),
                vertex_normals=(
                    tuple(self.vertex_normals[f[2] - 1] for f in face)
                    if self.vertex_normals
                    else None
                ),
                light_dir=LIGHT_DIR,
                lighting=lighting,
                rotation=self.rotation,
                **kwargs,
            )

        for face in self.faces:
            render_face(face)
        if outfile is not None:
            img.save(outfile)
        return img

    @classmethod
    def open(cls, filename, scale=1, textures={}):
        vertices, faces, texture_vertices, vertex_normals = [], [], [], []
        with open(filename) as f:
            for line in f:
                if not line.strip():
                    continue
                linetype, *args = line.split()
                if linetype == "v":
                    vertices.append(vec3.Vec3(*(-scale * float(i) for i in args)))
                elif linetype == "vt":
                    texture_vertices.append(vec3.Vec3(*(float(i) for i in args)))
                elif linetype == "vn":
                    vertex_normals.append(vec3.Vec3(*(float(i) for i in args)))
                elif linetype == "f":
                    faces.append([[int(i) for i in a.split("/")] for a in args])
        return cls(vertices, texture_vertices, vertex_normals, faces, textures)

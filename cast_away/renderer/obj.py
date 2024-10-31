from . import image, vec3, cCore
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
        self.defaults = {}
        (
            self._projection,
            self._viewport,
            self._projection_x_viewport,
            self._i_viewport,
            self._i_projection,
        ) = (None, None, None, None, None)
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
        self._projection = vec3.Matrix.projection(self.defaults.get("cam_z", CAM_Z))
        self._viewport = vec3.Matrix.viewport(
            imw / 8, imh / 8, imw * 3 / 4, imh * 3 / 4
        )
        self._i_projection = vec3.Matrix.inverse_projection(
            self.defaults.get("cam_z", CAM_Z)
        )
        self._i_viewport = vec3.Matrix.inverse_viewport(
            imw / 8, imh / 8, imw * 3 / 4, imh * 3 / 4
        )
        print(self._viewport, f"{imw/8},{imh/8},{imw*3/4},{imh*3/4}")
        self._projection_x_viewport = self._viewport @ self._projection

    def clone(self, copy_transforms=False):
        new_objfile = ObjFile(
            self.vertices,
            self.texture_vertices,
            self.vertex_normals,
            self.faces,
            self.textures,
        )
        new_objfile._cached_img = self._cached_img
        new_objfile._imw, new_objfile._imh = (self._imw, self._imh)
        if copy_transforms:
            new_objfile.translate(self.translation)
            new_objfile.rotate(self.rotation)
        return new_objfile

    def cleanup(self):
        self.textures={}
        self.vertices=[]
        self.vertex_normals=[]

    def add_texture(self, texture_type, texture_file):
        if isinstance(texture_file, str):
            self.textures[texture_type] = cCore.Texture.from_ppm(texture_file)
        else:
            self.textures[texture_type] = texture_file

    def calculate_centerpoint(self):

        vertex_sum = sum(self.vertices, vec3.Vec3(0, 0, 0))
        return vertex_sum / len(self.vertices)

    def translate(self, delta):
        self.translation += delta
        *self.vertices, self.centerpoint = [
            vert + delta for vert in (*self.vertices, self.centerpoint)
        ]

    def set_defaults(self, **dfs):
        self.defaults.update(dfs)

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

    def render(
        self,
        imw=None,
        imh=None,
        outfile=None,
        screen=None,
        lighting="phong",
        chunk_size=1,
        zbuffer=None,
        backface_culling=True,
        cam_z=None,
        **kwargs,
    ):
        if zbuffer is None:
            zbuffer = {}
        cam_z = cam_z or self.defaults.get("cam_z", CAM_Z)
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
        projection = (
            self._projection if cam_z == self.defaults.get("cam_z", CAM_Z) else None
        ) or vec3.Matrix.projection(cam_z)
        viewport = self._viewport or vec3.Matrix.viewport(
            imw / 8, imh / 8, imw * 3 / 4, imh * 3 / 4
        )
        projection_x_viewport = self._projection_x_viewport or (viewport @ projection)

        def render_face(face):
            world_coords = tuple(self.vertices[f[0] - 1] for f in face)
            if any(coor.z < NEAR_PLANE for coor in world_coords):
                return
            screen_coords = tuple(projection_x_viewport @ wc for wc in world_coords)
            n = (
                (world_coords[2] - world_coords[0])
                .cross(world_coords[1] - world_coords[0])
                .normalized()
            )
            if n.dot(LIGHT_DIR) <= 0 and backface_culling:
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

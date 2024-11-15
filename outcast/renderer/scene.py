from . import cCore


class Scene:
    def __init__(self):
        self.objects = set()
        self.imh = 0
        self.imw = 0
        self._rimg = None
        self.screen = None
        self.default_kwargs = {}
        self.defaults = {}

    def render(
        self,
        imw=None,
        imh=None,
        outfile=None,
        screen=None,
        chunk_size=1,
        **kwargs,
    ):

        zbuffer = cCore.Matrix.empty((imw or self.imw) + 1, (imh or self.imh) + 1)
        for obj in self.objects:
            obj.render(
                imw,
                imh,
                outfile,
                screen,
                chunk_size=chunk_size,
                zbuffer=zbuffer,
                **kwargs,
                **self.default_kwargs,
            )

    def set_kwargs(self, **kwargs):
        self.default_kwargs.update(kwargs)

    def set_defaults(self, **dfs):
        self.defaults.update(dfs)

    def add_obj(self, ob):
        if self._rimg:
            imw, imh, kwargs = self._rimg
            ob.set_defaults(**self.defaults)
            ob.set_render_image(imw, imh, **kwargs)
        self.objects.add(ob)

    def call_all(self, function_name, *args, **kwargs):
        for ob in self.objects:
            getattr(ob, function_name)(*args, **kwargs)

    def set_render_image(self, imw, imh, **kwargs):
        self.imw = imw
        self.imh = imh
        self.screen = kwargs.get("screen")
        self._rimg = (imw, imh, kwargs)
        self.call_all("set_render_image", imw, imh, **kwargs)

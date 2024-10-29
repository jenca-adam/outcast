from setuptools import setup, Extension

module = Extension(
    "spongia.renderer.cCore",
    sources=["spongia/renderer/cCore.c"],
    extra_compile_args=["-O0"],

)

setup(
    name="spngia.renderer.cCore",
    version="0.0",
    ext_modules=[module],
    install_requires=["pygame","pygame-gui", "coloredlogs"],
)

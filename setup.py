from setuptools import setup, Extension, find_packages

setup(
    name="outcast",
    version="0.0",
    description="game",
    packages=find_packages(include=["outcast", "outcast.renderer"]),
    install_requires=["pygame-ce", "pygame-gui", "coloredlogs"],
    ext_modules=[
        Extension(
            "outcast.renderer.cCore",
            sources=["outcast/renderer/cCore.c"],
            extra_compile_args=["-O0"],
        )
    ],
)

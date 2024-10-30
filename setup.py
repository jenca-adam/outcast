from setuptools import setup, Extension, find_packages

setup(
    name="cast_away",
    version="0.0",
    description="game",
    packages=find_packages(include=["cast_away", "cast_away.renderer"]),
    install_requires=["pygame-ce", "pygame-gui", "coloredlogs"],
    ext_modules=[
        Extension(
            "cast_away.renderer.cCore",
            sources=["cast_away/renderer/cCore.c"],
            extra_compile_args=["-O0"],
        )
    ],
)

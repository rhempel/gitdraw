from distutils.core import setup

setup(
    name="gitdraw",
    packages=["gitdraw"],
    version="1.0",
    license="MIT",
    description="A simple tool for generating git graphs",
    author="Samuel Broster",
    author_email="s.h.broster@gmail.com",
    url="https://gitlab.com/broster/gitdraw",
    download_url="https://gitlab.com/broster/gitdraw/-/archive/V1.0.0/gitdraw-V1.0.0.tar.gz",
    keywords=["git", "graph", "draw", "svg"],
    install_requires=["jinja2", "parsimonious", "palettable"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
    ],
)

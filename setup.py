import os
import setuptools

# Crete new tag & update download url & version
# Run:
# venv\Scripts\python.exe setup.py sdist bdist_wheel
# venv\Scripts\twine.exe upload dist/*

if not os.environ.get("CI_COMMIT_TAG"):
    exit()

version = os.environ["CI_COMMIT_TAG"]

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gitdraw",
    packages=["gitdraw"],
    version=version,
    license="MIT",
    description="A simple tool for generating git graphs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Samuel Broster",
    author_email="s.h.broster@gmail.com",
    url="https://gitlab.com/broster/gitdraw",
    download_url="https://gitlab.com/broster/gitdraw/-/archive/1.0.1/gitdraw-1.0.1.tar.gz",
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

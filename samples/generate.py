#!/uar/bin/python3.7
# -*- coding: utf-8 -*-
"""Create images from all samples"""
from typing import Iterator, Tuple
from glob import glob
from gitdraw import parse_file, Repo, Drawer, SvgDrawingTool

SAMPLE_DIR = "samples"


def generate_img(inpath: str, outpath: str, dark_mode: bool = False):
    """Generate an image from a sample file"""
    repo = parse_file(inpath, Repo())
    drawer = Drawer(dark_mode)
    output = drawer.draw_repo(repo, SvgDrawingTool())

    with open(outpath, "w") as outfile:
        outfile.write(output)


def samples(directory: str, dark_mode: bool = False) -> Iterator[Tuple[str, str]]:
    """Find sample files and the determine name of matching image"""
    sample_files = glob(f"{directory}/*.txt")
    if dark_mode:
        out_files = [f"{s[:-4]}_dm.svg" for s in sample_files]
    else:
        out_files = [f"{s[:-4]}.svg" for s in sample_files]
    return zip(sample_files, out_files)


def main():
    """The main operation"""
    for infile, outfile in samples(SAMPLE_DIR):
        generate_img(infile, outfile)

    for infile, outfile in samples(SAMPLE_DIR, dark_mode=True):
        generate_img(infile, outfile, dark_mode=True)


if __name__ == "__main__":
    exit(main())

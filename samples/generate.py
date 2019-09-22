#!/uar/bin/python3.7
# -*- coding: utf-8 -*-
"""Create images from all samples"""
from typing import Iterator, Tuple
from glob import glob
from gitdraw import parse_file, Repo, Drawer, SvgDrawingTool

SAMPLE_DIR = "samples"


def generate_img(inpath: str, outpath: str):
    """Generate an image from a sample file"""
    repo = parse_file(inpath, Repo())
    drawer = Drawer()
    output = drawer.draw_repo(repo, SvgDrawingTool())

    with open(outpath, "w") as outfile:
        outfile.write(output)


def samples(directory: str) -> Iterator[Tuple[str, str]]:
    """Find sample files and the determine name of matching image"""
    sample_files = glob(f"{directory}/*.txt")
    out_files = [f"{s[:-4]}.svg" for s in sample_files]
    return zip(sample_files, out_files)


def main():
    """The main operation"""
    for infile, outfile in samples(SAMPLE_DIR):
        generate_img(infile, outfile)


if __name__ == "__main__":
    exit(main())

#!/uar/bin/python3.7
# -*- coding: utf-8 -*-
"""Prototype script that creates an SVG image of a git `Repo`

ToDo:
  * wrap with command line args
  * accept and parse an input file
  * testing of Drawer and SvgDrawingTool
"""
from gitdraw.draw import Drawer
from gitdraw.repo import Repo
from gitdraw.svg_draw import SvgDrawingTool

if __name__ == "__main__":
    REPO = Repo()
    REPO.branch("gitdraw")
    REPO.checkout("gitdraw")
    REPO.commit()
    REPO.branch("feature")
    REPO.checkout("feature")
    REPO.commit()
    REPO.checkout("master")
    REPO.commit()
    REPO.merge("gitdraw")

    DRAWER = Drawer()
    OUT = DRAWER.draw_repo(REPO, SvgDrawingTool())

    with open("img.svg", "w") as f:
        f.write(OUT)

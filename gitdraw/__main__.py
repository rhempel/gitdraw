from gitdraw.draw import Drawer
from gitdraw.repo import Repo
from gitdraw.svg_draw import SvgDrawingTool

if __name__ == "__main__":
    r = Repo()
    r.branch("test")
    r.checkout("test")
    r.commit()
    r.checkout("master")
    r.commit()
    r.merge("test")  # Todo see commit but not merge

    d = Drawer()
    o = d.draw_repo(r, SvgDrawingTool())

    with open("img.svg", "w") as f:
        f.write(o)

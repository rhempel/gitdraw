from dataclasses import dataclass, field
from jinja2 import Environment, PackageLoader, select_autoescape
from typing import List

from gitdraw.draw import DrawingTool, DrawBranch, DrawCommit, DrawPoint, DrawMerge, SEP

env = Environment(
    loader=PackageLoader("gitdraw", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


@dataclass
class SvgPath:
    move: DrawPoint
    line: DrawPoint = None
    curve: (DrawPoint, DrawPoint, DrawPoint) = None

    @property
    def svg(self):
        m = self.move
        if self.line:
            ln = self.line
            return f"M{m.x},{m.y} L{ln.x},{ln.y}"
        c1, c2, c3 = self.curve
        return f"M{m.x},{m.y} C{c1.x},{c1.y} {c2.x},{c2.y} {c3.x},{c3.y}"


@dataclass
class SvgMerge(DrawMerge):
    @property
    def path(self) -> SvgPath:
        sx, sy = self.start.x, self.start.y
        ey = self.end.y
        return SvgPath(
            self.end, curve=(DrawPoint(sx, ey), DrawPoint(sx, ey), DrawPoint(sx, sy))
        )


@dataclass
class SvgLabel:
    position: DrawPoint
    width: int


@dataclass
class SvgBranch(DrawBranch):
    merges: List[SvgMerge]
    commits: List[DrawCommit] = field(default_factory=list)
    max_y: int = None
    max_x: int = None

    @property
    def label(self) -> SvgLabel:
        first_commit = self.commits[0]
        return SvgLabel(
            DrawPoint(self.max_x, first_commit.position.y), len(self.name) * 7
        )

    @property
    def start_path(self) -> SvgPath:
        first_commit = self.commits[0]
        fx, fy = first_commit.position.x, first_commit.position.y
        sy = self.start.y
        return SvgPath(
            self.start, curve=(DrawPoint(fx, sy), DrawPoint(fx, sy), DrawPoint(fx, fy))
        )

    @property
    def middle_path(self) -> SvgPath:
        line_start = self.commits[0].position
        line_end = self.commits[-1].position
        return SvgPath(line_start, line=line_end)

    @property
    def end_path(self) -> SvgPath:
        last_commit = self.commits[-1]
        if any(last_commit.position == m.start for m in self.merges):
            # If the last commit was merged don't extend the branch
            return None
        return SvgPath(
            last_commit.position, line=DrawPoint(last_commit.position.x, self.max_y)
        )


class SvgDrawingTool(DrawingTool):
    def __init__(self):
        super(SvgDrawingTool, self).__init__()
        self._branches = []
        self._template = env.get_template("git_svg.j2")
        self._max_y = 0
        self._max_x = 0

    def branch(self, branch: DrawBranch):
        self._branches.append(
            SvgBranch(
                merges=[SvgMerge(m.start, m.end) for m in branch.merges],
                name=branch.name,
                start=branch.start,
                colour=branch.colour,
            )
        )

    def commit(self, commit: DrawCommit):
        branch, = [b for b in self._branches if b.name == commit.branch.name]
        branch.commits.append(commit)
        self._max_y = max([self._max_y, commit.position.y])
        self._max_x = max([self._max_x, commit.position.x])

    def render(self):
        for branch in self._branches:
            branch.max_y = self._max_y + SEP
            branch.max_x = self._max_x + SEP

        return self._template.render(branches=self._branches)

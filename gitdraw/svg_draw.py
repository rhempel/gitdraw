# -*- coding: utf-8 -*-
"""A concrete `DrawingTool` for creating SVG graphs

TODO support '/' in branch names
"""
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from jinja2 import Environment, PackageLoader, select_autoescape

from gitdraw.draw import DrawingTool, DrawBranch, DrawCommit, DrawPoint, DrawMerge, SEP

ENV = Environment(
    loader=PackageLoader("gitdraw", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


class PathError(Exception):
    """Raised for errors with `SvgPath"""


@dataclass
class SvgPath:
    """Representation of an SVG Path object.

    For example:
    * Lines: M0,10 L20,20
    * Curves: C0,10 C10,10 10,20 20,20
    """

    move: DrawPoint
    line: Optional[DrawPoint] = None
    curve: Optional[Tuple[DrawPoint, DrawPoint, DrawPoint]] = None

    @property
    def svg(self) -> str:
        """Return the SVG representation of the path"""
        if (self.line is None) == (self.curve is None):
            raise PathError("SvgPath must have specify 'line' or 'curve'")

        move = self.move
        if self.line:
            line = self.line
            return f"M{move.x},{move.y} L{line.x},{line.y}"

        c1, c2, c3 = self.curve  # type: ignore pylint: disable=C0103,E0633

        # Figure out the curve direction and create the correct arc
        #
        radius = SEP/2

        if ((c3.y - move.y) > 0):
            if ((c3.x - move.x) > 0):
                # Generate an arc that goes right then down (new branch)
                return f"M{move.x},{move.y} L{c3.x-radius},{move.y} A{radius} {radius}, 0, 0, 1, {c3.x} {move.y+radius} L{c3.x},{c3.y}"

        elif ((c3.y - move.y) < 0):
            if ((c3.x - move.x) > 0):
                # Generate an arc that goes down then left (merge from branch)
                return f"M{move.x},{move.y} L{c3.x-radius},{move.y} A{radius} {radius}, 0, 0, 0, {c3.x} {move.y-radius} L{c3.x},{c3.y}"
            else:
                # Generate an arc that goes down then right (merge to branch)
                return f"M{move.x},{move.y} L{c3.x+radius},{move.y} A{radius} {radius}, 0, 0, 1, {c3.x} {move.y-radius} L{c3.x},{c3.y}"

        else:
            return f""


@dataclass
class SvgMerge(DrawMerge):
    """A curved SVG path representing a merge between branches"""

    @property
    def path(self) -> SvgPath:
        """The Path representing the Merge"""
        sx, sy = self.start.x, self.start.y  # pylint: disable=C0103
        ey = self.end.y  # pylint: disable=C0103
        return SvgPath(
            self.end, curve=(DrawPoint(sx, ey), DrawPoint(sx, ey), DrawPoint(sx, sy))
        )


@dataclass
class SvgLabel:
    """The position an size of an SVG label"""

    position: DrawPoint
    width: int


@dataclass
class SvgBranch(DrawBranch):
    """SVG representation of commits (and lines) of a branch"""

    commits: List[DrawCommit] = field(default_factory=list)
    max_y: int = 0
    max_x: int = 0

    @property
    def label(self) -> SvgLabel:
        """The position and size of the branches label"""
        first_commit = self.commits[0]  # pylint: disable=E1136
        return SvgLabel(
            DrawPoint(self.max_x, first_commit.position.y), len(self.name) * 7
        )

    @property
    def start_path(self) -> SvgPath:
        """The initial part of the branch

        This is a line drawn from where the branch starts to its
        first commit"""
        first = self.commits[0]  # pylint: disable=E1136
        fx, fy = (first.position.x, first.position.y)  # pylint: disable=C0103
        sy = self.start.y  # pylint: disable=C0103
        return SvgPath(
            self.start, curve=(DrawPoint(fx, sy), DrawPoint(fx, sy), DrawPoint(fx, fy))
        )

    @property
    def middle_path(self) -> SvgPath:
        """The middle part of the branch (connecting first and last commit)"""
        line_start = self.commits[0].position  # pylint: disable=E1136
        line_end = self.commits[-1].position  # pylint: disable=E1136
        return SvgPath(line_start, line=line_end)

    @property
    def end_path(self) -> Optional[SvgPath]:
        """The end of the branch

        A branch only has an end path if it has unmerged commits. Where
        all commits are merged, the last commit has a line drawn from
        it as part of the associated merge."""
        last_commit = self.commits[-1]  # pylint: disable=E1136
        if any(last_commit.position == m.start for m in self.merges):
            # If the last commit was merged don't extend the branch
            return None
        return SvgPath(
            last_commit.position, line=DrawPoint(last_commit.position.x, self.max_y)
        )


class SvgDrawingTool(DrawingTool):
    """A tool for creating an SVG image representing a git repository"""

    def __init__(self):
        super(SvgDrawingTool, self).__init__()
        self._branches = []
        self._template = ENV.get_template("git_svg.j2")
        self._max_y = 0
        self._max_x = 0
        self._rotate_image = 0
        self._rotate_label = 0
        self._rotate_commit = 0

    def branch(self, branch: DrawBranch):
        """Add a branch to be drawn"""
        self._branches.append(
            SvgBranch(
                merges=[SvgMerge(m.start, m.end) for m in branch.merges],
                idx=branch.idx,
                name=branch.name,
                start=branch.start,
                colour=branch.colour,
            )
        )

    def commit(self, commit: DrawCommit):
        """Add a commit to be drawn"""
        branch, = [b for b in self._branches if b.name == commit.branch.name]
        branch.commits.append(commit)
        self._max_y = max([self._max_y, commit.position.y])
        self._max_x = max([self._max_x, commit.position.x])

    def render(self, dark_mode: bool = False, horizontal_mode: bool = False) -> str:
        """Draw all branches and commits added so far"""
        for branch in self._branches:
            branch.max_y = self._max_y + SEP
            branch.max_x = self._max_x + SEP

        if horizontal_mode:
          self._rotate_image=-90
          self._rotate_label=45
          self._rotate_commit=90

        return self._template.render(
            branches=self._branches,
            dark_mode=dark_mode,
            max_x=self._max_x,
            max_y=self._max_y,
            rotate_image=self._rotate_image,
            rotate_label=self._rotate_label,
            rotate_commit=self._rotate_commit,
        )

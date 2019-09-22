# -*- coding: utf-8 -*-
"""Generic class for drawing git graphs

A concrete implementation of the `DrawingTool` can be passed
to the `Drawer` to draw a graphical representation of the
git `Repo`
"""
from abc import ABC, abstractmethod
from itertools import cycle
from dataclasses import dataclass
from typing import List, TypeVar, Generator
from palettable.colorbrewer.qualitative import Dark2_8  # type: ignore
from palettable.tableau import TableauMedium_10  # type: ignore

from gitdraw.repo import Repo, Branch, Commit, MergeCommit

SEP = 30


@dataclass
class DrawPoint:
    """Coordinates to a location"""

    x: int
    y: int


@dataclass
class DrawMerge:
    """The merge line drawn from a commit in one branch to another"""

    start: DrawPoint
    end: DrawPoint


@dataclass
class DrawBranch:
    """A branch line (and associated merges into other branches)"""

    name: str
    idx: int
    start: DrawPoint
    colour: str
    merges: List[DrawMerge]


@dataclass
class DrawCommit:
    """The position of a commit"""

    name: str
    idx: int
    position: DrawPoint
    branch: DrawBranch


class DrawingTool(ABC):
    """A base class implementation for a tool that draws a git repo"""

    @abstractmethod
    def branch(self, branch: DrawBranch):
        """Adds a branch into the Repo"""

    @abstractmethod
    def commit(self, commit: DrawCommit):
        """Adds a commit into the Repo"""

    @abstractmethod
    def render(self, dark_mode: bool = False) -> str:
        """Draws the git repo"""


DT = TypeVar("DT", bound=DrawingTool)
MC = TypeVar("MC", bound=MergeCommit)


class Drawer:  # pylint: disable=R0903
    """Uses a `DrawingTool` to draw a `Repo`"""

    def __init__(self, dark_mode=False):
        self._tool = None
        self._dark_mode = dark_mode
        self._branches = {}
        self._commits = []
        self._colours = colours(dark_mode)

    def draw_repo(self, repo: Repo, drawer: DT) -> str:
        """Draw a picture of a `Repo` using a `DrawingTool

        :param repo: The `Repo` to draw
        :param drawer: The `DrawingTool` to use to draw it
        """
        self._tool = drawer

        commits = [c for b in repo.branches.values() for c in b.commits]
        commits = sorted(commits, key=lambda x: x.idx)

        for commit in commits:
            if commit.branch.name not in self._branches:
                self._stage_branch(commit.branch)
            if isinstance(commit, MergeCommit):
                self._add_merge(commit)
            self._stage_commit(commit)

        for branch in sorted(self._branches.values(), key=lambda x: x.idx):
            self._tool.branch(branch)
        for commit in self._commits:
            self._tool.commit(commit)

        return self._tool.render(self._dark_mode)

    def _stage_branch(self, branch: Branch):
        """Create a `DrawBranch` object ready for adding to the `DrawingTool`

        :param branch: The `Branch` used to create the `DrawingBranch`
        """
        branch_commit = branch.branch_commit
        # master doesn't have a branch commit, just it's first commit
        branch_commit = branch_commit if branch_commit else branch.commits[0]

        draw_branch = DrawBranch(
            branch.name,
            branch.idx,
            DrawPoint(branch_commit.branch.idx * SEP, branch_commit.idx * SEP),
            next(self._colours),
            [],
        )
        self._branches[branch.name] = draw_branch

    def _add_merge(self, commit: MC):
        """Add a `DrawMerge` to a `DrawBranch`

        Given a commit associated with a Merge, find the parent commit
        in the branch being merged. Use those two commit to represent
        the `DrawMerge`.

        :param commit: The merge commit
        """
        merge_commit = commit.merge_commit
        draw_branch = self._branches[merge_commit.branch.name]
        draw_branch.merges.append(
            DrawMerge(
                DrawPoint(merge_commit.branch.idx * SEP, merge_commit.idx * SEP),
                DrawPoint(commit.branch.idx * SEP, commit.idx * SEP),
            )
        )

    def _stage_commit(self, commit: Commit):
        """Create a `DrawCommit` ready to be added to the `DrawingTool`

        :param commit: The commit to be added
        """

        self._commits.append(
            DrawCommit(
                commit.name,
                commit.idx,
                DrawPoint(commit.branch.idx * SEP, commit.idx * SEP),
                self._branches[commit.branch.name],
            )
        )


def colours(dark_mode=False) -> Generator[str, None, None]:
    """Generate a repeating list of colours to use for branches

    The first colour is reserved exclusively for the main branch
    all other colours can be repeated.
    """
    colours = Dark2_8.hex_colors if dark_mode else TableauMedium_10.hex_colors
    main_colour, *other_colours = colours
    another_colour = cycle(other_colours)
    yield main_colour
    while True:
        yield next(another_colour)  # pylint: disable=R1708

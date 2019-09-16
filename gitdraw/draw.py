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

from gitdraw.repo import Repo, Branch, Commit

SEP = 50

COLOURS = [
    "#002b36",
    "#268bd2",
    "#859900",
    "#cb4b16",
    "#2aa198",
    "#dc322f",
    "#d33682",
    "#6c71c4",
    "#b58900",
]


@dataclass
class DrawPoint:
    x: int
    y: int


@dataclass
class DrawMerge:
    start: DrawPoint
    end: DrawPoint


@dataclass
class DrawBranch:
    name: str
    start: DrawPoint
    colour: str
    merges: List[DrawMerge]


@dataclass
class DrawCommit:
    name: str
    position: DrawPoint
    branch: DrawBranch


class DrawingTool(ABC):
    @abstractmethod
    def branch(self, branch: DrawBranch):
        pass

    @abstractmethod
    def commit(self, commit: DrawCommit):
        pass

    @abstractmethod
    def render(self):
        pass


DT = TypeVar("DT", bound=DrawingTool)


class Drawer:
    def __init__(self):
        self._tool = None
        self._branches = {}
        self._commits = []
        self._colours = colours()

    def draw_repo(self, repo: Repo, drawer: DT) -> str:
        self._tool = drawer

        commits = [c for b in repo.branches.values() for c in b.commits]
        commits = sorted(commits, key=lambda x: x.idx)

        for commit in commits:
            if commit.branch.name not in self._branches:
                self.stage_branch(commit.branch)
            if len(commit.parents) == 2:
                self.add_merge(commit)
            self.stage_commit(commit)

        for _, branch in self._branches.items():
            self._tool.branch(branch)
        for commit in self._commits:
            self._tool.commit(commit)

        return self._tool.render()

    def stage_branch(self, branch: Branch):
        branch_commit = branch.branch_commit
        # master doesn't have a branch commit, just it's first commit
        branch_commit = branch_commit if branch_commit else branch.commits[0]

        draw_branch = DrawBranch(
            branch.name,
            DrawPoint(branch_commit.branch.idx * SEP, branch_commit.idx * SEP),
            next(self._colours),
            [],
        )
        self._branches[branch.name] = draw_branch

    def add_merge(self, commit: Commit):
        merge_commit, = [p for p in commit.parents if p.branch != commit.branch]
        draw_branch = self._branches[merge_commit.branch.name]
        draw_branch.merges.append(
            DrawMerge(
                DrawPoint(merge_commit.branch.idx * SEP, merge_commit.idx * SEP),
                DrawPoint(commit.branch.idx * SEP, commit.idx * SEP),
            )
        )

    def stage_commit(self, commit: Commit):
        self._commits.append(
            DrawCommit(
                commit.name,
                DrawPoint(commit.branch.idx * SEP, commit.idx * SEP),
                commit.branch,
            )
        )


def colours() -> Generator[str, None, None]:
    main_colour, *other_colours = COLOURS
    another_colour = cycle(other_colours)
    yield main_colour
    while True:
        yield next(another_colour)  # pylint: disable=R1708

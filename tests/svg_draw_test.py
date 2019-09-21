# -*- coding: utf-8 -*-
# pylint: disable=W0621
"""Testing of the SVG drawing objects"""
import pytest
from pytest_steps import test_steps
from tests.context import (
    SvgPath,
    PathError,
    DrawPoint,
    SvgMerge,
    SvgBranch,
    DrawCommit,
    SvgLabel,
    SvgDrawingTool,
    DrawBranch,
)


def test_svg_path_line():
    """Test an `SvgPath` returns lines correctly"""
    line = SvgPath(DrawPoint(0, 10), line=DrawPoint(50, 60))

    assert line.svg == "M0,10 L50,60"


def test_svg_path_curve():
    """Test `SvgPath` returns curves correctly"""
    curve = SvgPath(
        DrawPoint(0, 10),
        curve=(DrawPoint(20, 30), DrawPoint(40, 50), DrawPoint(60, 70)),
    )

    assert curve.svg == "M0,10 C20,30 40,50 60,70"


def test_invalid_svgpath():
    """Test `SvgPath` raises an error if invalid"""
    bad = SvgPath(
        DrawPoint(0, 10),
        line=DrawPoint(50, 60),
        curve=(DrawPoint(20, 30), DrawPoint(40, 50), DrawPoint(60, 70)),
    )

    with pytest.raises(PathError):
        bad.svg


def test_svg_merge():
    """Test an `SvgMerge` path is the expected `SvgPath`"""
    merge = SvgMerge(DrawPoint(0, 0), DrawPoint(100, 100))

    assert merge.path == SvgPath(
        DrawPoint(100, 100),
        curve=(DrawPoint(0, 100), DrawPoint(0, 100), DrawPoint(0, 0)),
    )


@test_steps("Branch not merged", "Branch merged")
def test_svg_branch():
    """Test an `SvgBranch` looks sensible"""
    branch = SvgBranch(
        name="test/branch",
        idx=4,
        start=DrawPoint(0, 10),
        colour="blue",
        merges=[SvgMerge(DrawPoint(0, 0), DrawPoint(100, 100))],
        commits=[],
        max_y=100,
        max_x=110,
    )
    branch.commits = [DrawCommit("A", 1, DrawPoint(0, 10), branch)]
    assert branch.label == SvgLabel(position=DrawPoint(x=110, y=10), width=77)
    assert branch.start_path == SvgPath(
        move=DrawPoint(x=0, y=10),
        line=None,
        curve=(DrawPoint(x=0, y=10), DrawPoint(x=0, y=10), DrawPoint(x=0, y=10)),
    )
    assert branch.middle_path == SvgPath(
        move=DrawPoint(x=0, y=10), line=DrawPoint(x=0, y=10), curve=None
    )
    assert branch.end_path == SvgPath(
        move=DrawPoint(x=0, y=10), line=DrawPoint(x=0, y=100), curve=None
    )
    yield

    branch.merges.append(SvgMerge(DrawPoint(0, 10), DrawPoint(100, 100)))
    assert branch.end_path is None
    yield


def test_svg_drawing_tool():
    tool = SvgDrawingTool()
    branch = DrawBranch(
        name="test/branch",
        idx=4,
        start=DrawPoint(0, 10),
        colour="blue",
        merges=[SvgMerge(DrawPoint(0, 0), DrawPoint(100, 100))],
    )

    commit = DrawCommit("A", 1, DrawPoint(0, 10), branch)

    tool.branch(branch)
    tool.commit(commit)
    assert isinstance(tool.render(), str)

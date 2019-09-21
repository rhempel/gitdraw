# -*- coding: utf-8 -*-
# pylint: disable=C0413,W0611
"""Common testing environment for use with pytest"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from gitdraw.repo import Repo, BranchException, MergeCommit
from gitdraw.draw import DrawingTool, Drawer, DrawBranch, DrawCommit, DrawPoint
from gitdraw.svg_draw import (
    SvgPath,
    PathError,
    SvgMerge,
    SvgBranch,
    SvgLabel,
    SvgDrawingTool,
)
from gitdraw.parser import (
    GitVisitor,
    GitParseError,
    InvalidGitCmd,
    parse_string,
    parse_file,
)

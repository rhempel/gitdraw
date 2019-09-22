# -*- coding: utf-8 -*-
# pylint: disable=W0621
"""Testing of the `Drawing` object"""
from collections import namedtuple
from pytest_steps import test_steps, optional_step

from tests.context import DrawingTool, Repo, Drawer, DrawBranch, DrawCommit
import tests.example_repos as repos

BranchInfo = namedtuple(
    "BranchInfo", "name num_commits num_merges start", defaults=[None]
)


class MockDrawingTool(DrawingTool):
    """An object to test the DrawingTool API"""

    def __init__(self):
        self.branches = []
        self.commits = []
        super(MockDrawingTool, self).__init__()

    def branch(self, branch: DrawBranch):
        """Adds a branch into the Repo"""
        self.branches.append(branch)

    def commit(self, commit: DrawCommit):
        """Adds a commit into the Repo"""
        self.commits.append(commit)

    def render(self, dark_mode: bool = False) -> str:
        """Draws the git repo"""
        return "rendered"

    def __str__(self):
        return f"MockDrawingTool:\n {self.branches}\n {self.commits}"

    def __repr__(self):
        return str(self)


def _commits_aligned_and_ordered(commits):
    """Verify commits are aligned vertically and ordered horizontally

    :param commits: An ordered list of commits to verify
    """
    for idx, commit in enumerate(commits):
        for other_commit in commits[idx + 1 :]:
            assert commit.position.x == other_commit.position.x
            assert commit.position.y < other_commit.position.y


def _branches_ordered(tool):
    """Verify branches are ordered vertically

    :param tool: The `DrawingTool` containing the branches
    """
    for idx, branch in enumerate(tool.branches):
        for other_branch in tool.branches[idx + 1 :]:
            # Get branch position by finding a commit associated with the branch
            branch_commit = next(c for c in tool.commits if c.branch == branch)
            other_commit = next(c for c in tool.commits if c.branch == other_branch)
            assert branch_commit.position.x < other_commit.position.x


def _validate_merges(merges):
    """Check a merge looks sensible"""
    for merge in merges:
        assert merge.start.x != merge.end.x
        assert merge.start.y < merge.end.y


def _validate_tool(tool, branch_info):
    """Verify a `DrawingTool` looks sensible

    :param tool: The `DrawingTool` to verify
    :param branch_info: A list of `BranchInfo` for branches in the tool
    """
    assert len(tool.branches) == len(branch_info)
    assert sorted(b.name for b in tool.branches) == sorted(b.name for b in branch_info)
    assert len(tool.commits) == sum(b.num_commits for b in branch_info)
    _branches_ordered(tool)

    for branch in tool.branches:
        branch_commits = [c for c in tool.commits if c.branch == branch]
        info = next(b for b in branch_info if b.name == branch.name)
        assert len(branch_commits) == info.num_commits
        assert len(branch.merges) == info.num_merges

        if info.start is not None:
            assert branch.start == info.start

        _commits_aligned_and_ordered(branch_commits)
        _validate_merges(branch.merges)


@test_steps(
    "Blank repository",
    "Make a commit",
    "Create a branch",
    "Checkout new branch",
    "Merge branch",
)
def test_basic_drawing(blank_repo):
    """"draw a repo with a single commit"""
    drawing_tool, drawer = MockDrawingTool(), Drawer()
    drawer.draw_repo(blank_repo, drawing_tool)
    main_start = drawing_tool.commits[0].position
    _validate_tool(
        drawing_tool,
        [BranchInfo(Repo.MAIN_BRANCH, num_commits=1, num_merges=0, start=main_start)],
    )
    yield

    blank_repo.commit()

    drawing_tool, drawer = MockDrawingTool(), Drawer()
    drawer.draw_repo(blank_repo, drawing_tool)
    _validate_tool(
        drawing_tool,
        [BranchInfo(Repo.MAIN_BRANCH, num_commits=2, num_merges=0, start=main_start)],
    )
    yield

    blank_repo.branch("test/branch")

    drawing_tool, drawer = MockDrawingTool(), Drawer()
    drawer.draw_repo(blank_repo, drawing_tool)
    branch_start = drawing_tool.commits[1].position
    _validate_tool(
        drawing_tool,
        [BranchInfo(Repo.MAIN_BRANCH, num_commits=2, num_merges=0, start=main_start)],
    )
    yield

    blank_repo.checkout("test/branch")
    blank_repo.commit()

    drawing_tool, drawer = MockDrawingTool(), Drawer()
    drawer.draw_repo(blank_repo, drawing_tool)
    _validate_tool(
        drawing_tool,
        [
            BranchInfo(Repo.MAIN_BRANCH, num_commits=2, num_merges=0, start=main_start),
            BranchInfo("test/branch", num_commits=1, num_merges=0, start=branch_start),
        ],
    )
    yield

    blank_repo.checkout(Repo.MAIN_BRANCH)
    blank_repo.merge("test/branch")

    drawing_tool, drawer = MockDrawingTool(), Drawer()
    drawer.draw_repo(blank_repo, drawing_tool)
    _validate_tool(
        drawing_tool,
        [
            BranchInfo(Repo.MAIN_BRANCH, num_commits=3, num_merges=0, start=main_start),
            BranchInfo("test/branch", num_commits=1, num_merges=1, start=branch_start),
        ],
    )
    yield


@test_steps(
    "Multiple merges",
    "Forward merge",
    "Multiple Branches",
    "Branch off branch",
    "Merge into empty branch",
)
def test_drawing_repos():
    """Draw a number of different repos"""
    with optional_step("Multiple Merges") as step:
        repo = repos.multiple_merges("test/branch")
        drawing_tool, drawer = MockDrawingTool(), Drawer()
        drawer.draw_repo(repo, drawing_tool)
        _validate_tool(
            drawing_tool,
            [
                BranchInfo(Repo.MAIN_BRANCH, num_commits=3, num_merges=0),
                BranchInfo("test/branch", num_commits=2, num_merges=2),
            ],
        )
    yield step

    with optional_step("Forward merge") as step:
        repo = repos.forward_merge("test/branch")
        drawing_tool, drawer = MockDrawingTool(), Drawer()
        drawer.draw_repo(repo, drawing_tool)
        _validate_tool(
            drawing_tool,
            [
                BranchInfo(Repo.MAIN_BRANCH, num_commits=3, num_merges=1),
                BranchInfo("test/branch", num_commits=2, num_merges=1),
            ],
        )
    yield step

    with optional_step("Multiple Branches") as step:
        repo = repos.multiple_branches(["test/branch/1", "test/branch/2"])
        drawing_tool, drawer = MockDrawingTool(), Drawer()
        drawer.draw_repo(repo, drawing_tool)
        _validate_tool(
            drawing_tool,
            [
                BranchInfo(Repo.MAIN_BRANCH, num_commits=4, num_merges=0),
                BranchInfo("test/branch/1", num_commits=1, num_merges=1),
                BranchInfo("test/branch/2", num_commits=1, num_merges=1),
            ],
        )
    yield step

    with optional_step("Branch off branch") as step:
        repo = repos.branch_off_branch(["test/branch/1", "test/branch/2"])
        drawing_tool, drawer = MockDrawingTool(), Drawer()
        drawer.draw_repo(repo, drawing_tool)
        _validate_tool(
            drawing_tool,
            [
                BranchInfo(Repo.MAIN_BRANCH, num_commits=3, num_merges=0),
                BranchInfo("test/branch/1", num_commits=1, num_merges=1),
                BranchInfo("test/branch/2", num_commits=1, num_merges=1),
            ],
        )
    yield step

    with optional_step("Merge into empty branch") as step:
        repo = repos.merge_into_empty_branch(["test/branch/1", "test/branch/2"])
        drawing_tool, drawer = MockDrawingTool(), Drawer()
        drawer.draw_repo(repo, drawing_tool)
        _validate_tool(
            drawing_tool,
            [
                BranchInfo(Repo.MAIN_BRANCH, num_commits=1, num_merges=0),
                BranchInfo("test/branch/1", num_commits=1, num_merges=0),
                BranchInfo("test/branch/2", num_commits=1, num_merges=1),
            ],
        )
    yield step

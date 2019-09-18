# -*- coding: utf-8 -*-
# pylint: disable=W0621
"""Testing of the `Drawing` object"""
import pytest
from .context import DrawingTool, Repo, Drawer, DrawBranch, DrawCommit


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

    def render(self) -> str:
        """Draws the git repo"""
        return "rendered"


def _commits_aligned_vertically_and_ordered_horizontally(commits):
    for idx, commit in enumerate(commits):
        for other_commit in commits[idx + 1 :]:
            assert commit.position.x == other_commit.position.x
            assert commit.position.y < other_commit.position.y


def _branches_ordered_vertically(tool):
    for idx, branch in enumerate(tool.branches):
        for other_branch in tool.branches[idx + 1 :]:
            branch_commit = next(c for c in tool.commits if c.branch == branch)
            other_commit = next(c for c in tool.commits if c.branch == other_branch)
            assert branch_commit.position.x < other_commit.position.x


def _validate_merges(merges):
    for merge in merges:
        assert merge.start.x != merge.end.x
        assert merge.start.y < merge.end.y


def _validate_tool(tool, num_branches, num_commits, num_merges):
    assert len(tool.branches) == num_branches
    assert len(tool.commits) == sum(num_commits)
    _branches_ordered_vertically(tool)

    for branch, num_commits, num_merges in zip(tool.branches, num_commits, num_merges):
        branch_commits = [c for c in tool.commits if c.branch == branch]
        assert len(branch_commits) == num_commits
        assert len(branch.merges) == num_merges
        _commits_aligned_vertically_and_ordered_horizontally(branch_commits)
        _validate_merges(branch.merges)


@pytest.fixture
def drawing_tool():
    """A concrete mocked out `DrawingTool`"""
    return MockDrawingTool()


@pytest.fixture
def repo():
    """An empty `Repo` used by tests"""
    return Repo()


@pytest.fixture
def drawer():
    """An empty `Drawer` used by tests"""
    return Drawer()


def test_basic_draw(drawer, drawing_tool, repo):
    """"draw a repo with a single commit"""
    drawer.draw_repo(repo, drawing_tool)

    assert len(drawing_tool.branches) == 1
    assert drawing_tool.branches[0].name == Repo.MAIN_BRANCH
    assert drawing_tool.branches[0].merges == []
    assert drawing_tool.branches[0].start == drawing_tool.commits[0].position

    assert len(drawing_tool.commits) == 1
    assert drawing_tool.commits[0].branch.name == drawing_tool.branches[0].name


def test_drawing_a_single_branch(drawer, drawing_tool, repo):
    """draw a repo with 5 commits"""
    for _ in range(4):
        repo.commit()
    drawer.draw_repo(repo, drawing_tool)

    assert len(drawing_tool.branches) == 1
    assert len(drawing_tool.commits) == 5

    # Checks commits are aligned vertically, and ordered horizontally
    for idx, commit in enumerate(drawing_tool.commits):
        for other_commit in drawing_tool.commits[idx + 1 :]:
            assert commit.position.x == other_commit.position.x
            assert commit.position.y < other_commit.position.y


def test_drawing_multiple_branches(drawer, drawing_tool, repo):
    """draw a repo with two branches"""
    repo.branch("test/branch")
    repo.checkout("test/branch")
    repo.commit()
    drawer.draw_repo(repo, drawing_tool)

    assert len(drawing_tool.branches) == 2
    assert len(drawing_tool.commits) == 2

    assert drawing_tool.branches[1].name == "test/branch"
    assert drawing_tool.branches[1].start == drawing_tool.commits[0].position

    main_commit_pos_x = drawing_tool.commits[0].position.x
    main_commit_pos_y = drawing_tool.commits[0].position.y
    branch_commit_pos_x = drawing_tool.commits[1].position.x
    branch_commit_pos_y = drawing_tool.commits[1].position.y

    assert main_commit_pos_x < branch_commit_pos_x
    assert main_commit_pos_y < branch_commit_pos_y


def test_drawing_a_merge(drawer, drawing_tool, repo):
    """draw a repo where one branches merges into another"""
    repo.branch("test/branch")
    repo.checkout("test/branch")
    repo.commit()
    repo.checkout("master")
    repo.merge("test/branch")

    drawer.draw_repo(repo, drawing_tool)

    assert len(drawing_tool.branches) == 2
    assert len(drawing_tool.commits) == 3

    assert not drawing_tool.branches[0].merges
    assert len(drawing_tool.branches[1].merges) == 1

    merge_start = drawing_tool.branches[1].merges[0].start
    merge_end = drawing_tool.branches[1].merges[0].end

    assert merge_start == drawing_tool.commits[1].position
    assert merge_end == drawing_tool.commits[2].position


def test_drawing_repo_with_multiple_merges(
    drawer, drawing_tool, repo_with_multiple_merges, branch_names
):
    drawer.draw_repo(repo_with_multiple_merges, drawing_tool)
    _validate_tool(drawing_tool, 2, [3, 3], [0, 2])


def test_drawing_repo_main_branch_merged_into_other_branch(
    drawer, drawing_tool, repo_main_branch_merged_into_other_branch, branch_names
):
    drawer.draw_repo(repo_main_branch_merged_into_other_branch, drawing_tool)
    _validate_tool(drawing_tool, 2, [4, 3], [1, 1])


def test_drawing_repo_with_multiple_branches(
    drawer, drawing_tool, repo_with_multiple_branches, branch_names
):
    drawer.draw_repo(repo_with_multiple_branches, drawing_tool)
    _validate_tool(drawing_tool, 3, [5, 2, 2], [0, 1, 1])


def test_drawing_repo_with_branch_off_branch(
    drawer, drawing_tool, repo_with_branch_off_branch, branch_names
):
    drawer.draw_repo(repo_with_branch_off_branch, drawing_tool)
    _validate_tool(drawing_tool, 3, [5, 2, 2], [0, 1, 1])

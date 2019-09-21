# -*- coding: utf-8 -*-
# pylint: disable=W0621
"""Testing of the `Repo` object"""
from functools import partial
from collections import namedtuple
import pytest
from pytest_steps import test_steps, optional_step

from tests.context import Repo, BranchException, MergeCommit
import tests.example_repos as repos

BranchInfo = namedtuple("BranchInfo", "name num_commits num_merges")


def _validate_repo(repo, branch_info):
    """Check that a repo looks sensible

    :param repo: The repo to check
    :param branch_info: a list of BranchInfo with details for each branch
    """
    assert [b.name for b in repo.branches.values()] == [b.name for b in branch_info]

    for name, branch in repo.branches.items():
        info = next(b for b in branch_info if b.name == name)
        _validate_branch(
            branch, branch.name, branch.branch_commit, info.num_commits, info.num_merges
        )

    commits = [c for b in repo.branches.values() for c in b.commits]
    for index, commit in enumerate(commits):
        for other_commit in commits[index + 1 :]:
            assert commit.idx != other_commit.idx
            assert commit.name != other_commit.name


def _validate_branch(branch, name, branch_commit, num_commits, num_merges):
    """Validate a branch has all the properties we'd expect

    :param branch: The branch to validate
    :param name: The name of the branch
    :param branch_commit: The commit the branch was created from
    :param num_commits: The number of commits on the branch
    :param num_merges: The number of merges into this branch
    """
    assert branch is not None
    assert branch.name is name
    assert branch.idx is not None
    assert branch.branch_commit == branch_commit
    assert len(branch.commits) == num_commits
    assert num_merges == len([c for c in branch.commits if isinstance(c, MergeCommit)])


def _validate_commit(commit, branch, parents):
    """Validate a commit has all the properties we'd expect

    :param commit: The commit to validate
    :param branch: The branch the commit is on
    :param parents: The commits parent commit
    """
    assert commit is not None
    assert commit.name is not None
    assert commit.idx is not None
    assert commit.branch == branch
    assert commit.parents == parents


@test_steps(
    "Blank repository",
    "Make a commit",
    "Create a branch",
    "Checkout new branch",
    "Merge branch",
)
def test_basic_mainline(blank_repo):
    """Test a new `Repo` object is as expected"""
    master = blank_repo.main_branch
    _validate_master = partial(
        _validate_branch, master, name=Repo.MAIN_BRANCH, branch_commit=None
    )
    _validate_master(num_commits=1, num_merges=0)
    _validate_commit(master.last_commit, branch=master, parents=[])
    yield

    blank_repo.commit()
    _validate_master(num_commits=2, num_merges=0)
    _validate_commit(master.last_commit, branch=master, parents=[master.commits[0]])
    yield

    blank_repo.branch("test/branch/1")
    first_branch = blank_repo.branches["test/branch/1"]
    _validate_first_branch = partial(
        _validate_branch,
        first_branch,
        name="test/branch/1",
        branch_commit=master.commits[1],
    )
    _validate_first_branch(num_commits=0, num_merges=0)
    yield

    blank_repo.checkout("test/branch/1")
    blank_repo.commit()
    _validate_first_branch(num_commits=1, num_merges=0)
    _validate_commit(
        first_branch.commits[0],
        branch=first_branch,
        parents=[first_branch.branch_commit],
    )
    yield

    blank_repo.checkout(master.name)
    blank_repo.merge("test/branch/1")
    _validate_master(num_commits=3, num_merges=1)
    _validate_commit(
        master.commits[2],
        branch=master,
        parents=[master.commits[1], first_branch.commits[0]],
    )
    yield


def test_100_commits():
    """Test that names and IDs remain unique over lots of commits"""
    repo_100_commits = repos.hundred_commits()
    master = repo_100_commits.main_branch

    for index, commit in enumerate(master.commits):
        assert commit.branch == master

        if index > 0:
            assert commit.parents == [master.commits[index - 1]]

        for other_commit in master.commits[index + 1 :]:
            assert commit.idx != other_commit.idx
            assert commit.name != other_commit.name


def test_duplicate_branch(blank_repo):
    """Test that it's not possible to create branches with the same name"""
    with pytest.raises(BranchException):
        blank_repo.branch(Repo.MAIN_BRANCH)

    assert len(blank_repo.branches) == 1


def test_failed_checkout(blank_repo):
    """Test checkout of a non-existent branch fails"""
    with pytest.raises(BranchException):
        blank_repo.checkout("bad/branch")


def test_dupe_merge(blank_repo):
    """Test that a branch can't be merged with itself"""
    with pytest.raises(BranchException):
        blank_repo.merge("master")


@test_steps("Can't merge empty branch", "Can merge after a commit")
def test_empty_branch(blank_repo):
    """Test that an empty branch can't be merged but a populated one can"""
    blank_repo.branch("test/branch")
    with pytest.raises(BranchException):
        blank_repo.merge("test/branch")
    yield

    blank_repo.checkout("test/branch")
    blank_repo.commit()
    blank_repo.checkout(Repo.MAIN_BRANCH)
    blank_repo.merge("test/branch")
    yield


@test_steps("Can't merge unchanged branch", "Can merge after a commit")
def test_duplicate_merge(blank_repo):
    """A branch can't be merged twice if it hasn't changed"""
    blank_repo.branch("test/branch")
    blank_repo.checkout("test/branch")
    blank_repo.commit()
    blank_repo.checkout(Repo.MAIN_BRANCH)
    blank_repo.merge("test/branch")

    with pytest.raises(BranchException):
        blank_repo.merge("test/branch")
    yield

    blank_repo.checkout("test/branch")
    blank_repo.commit()
    blank_repo.checkout(Repo.MAIN_BRANCH)
    blank_repo.merge("test/branch")
    yield


def test_merge_into_empty_branch(blank_repo):
    """Test an empty branch can still be merged into"""
    blank_repo.branch("test/branch/1")
    blank_repo.branch("test/branch/2")
    blank_repo.checkout("test/branch/1")
    blank_repo.commit()


@test_steps(
    "Multiple merges",
    "Forward merge",
    "Multiple Branches",
    "Branch off branch",
    "Merge into empty branch",
)
def test_scenarios(blank_repo):
    """Test a number of more complicated repositories"""
    with optional_step("Multiple Merges") as step:
        repo = repos.multiple_merges("test/branch")
        _validate_repo(
            repo,
            [
                BranchInfo(Repo.MAIN_BRANCH, num_commits=3, num_merges=2),
                BranchInfo("test/branch", num_commits=2, num_merges=0),
            ],
        )
    yield step

    with optional_step("Forward merge") as step:
        repo = repos.forward_merge("test/branch")
        _validate_repo(
            repo,
            [
                BranchInfo(Repo.MAIN_BRANCH, num_commits=3, num_merges=1),
                BranchInfo("test/branch", num_commits=2, num_merges=1),
            ],
        )
    yield step

    with optional_step("Multiple Branches") as step:
        repo = repos.multiple_branches(["test/branch/1", "test/branch/2"])
        _validate_repo(
            repo,
            [
                BranchInfo(Repo.MAIN_BRANCH, num_commits=4, num_merges=2),
                BranchInfo("test/branch/1", num_commits=1, num_merges=0),
                BranchInfo("test/branch/2", num_commits=1, num_merges=0),
            ],
        )
    yield step

    with optional_step("Branch off branch") as step:
        repo = repos.branch_off_branch(["test/branch/1", "test/branch/2"])
        _validate_repo(
            repo,
            [
                BranchInfo(Repo.MAIN_BRANCH, num_commits=3, num_merges=2),
                BranchInfo("test/branch/1", num_commits=1, num_merges=0),
                BranchInfo("test/branch/2", num_commits=1, num_merges=0),
            ],
        )
    yield step

    with optional_step("Merge into empty branch") as step:
        repo = repos.merge_into_empty_branch(["test/branch/1", "test/branch/2"])
        _validate_repo(
            repo,
            [
                BranchInfo(Repo.MAIN_BRANCH, num_commits=1, num_merges=0),
                BranchInfo("test/branch/1", num_commits=1, num_merges=1),
                BranchInfo("test/branch/2", num_commits=1, num_merges=0),
            ],
        )
    yield step

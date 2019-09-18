# -*- coding: utf-8 -*-
# pylint: disable=W0621
"""Testing of the `Repo` object"""
import pytest
from .context import Repo, BranchException


def branches(repo, branch_names, num_branches=0):
    branch_names = branch_names[:num_branches]
    return [repo.main_branch] + [repo.branches[name] for name in branch_names]


def _validate_repos(repo, branch_names, num_branches, num_commits, num_merges):
    all_branches = branches(repo, branch_names, num_branches)

    for branch, num_commits, num_merges in zip(all_branches, num_commits, num_merges):
        assert len(branch.commits) == num_commits
        assert len([c for c in branch.commits if len(c.parents) == 2]) == num_merges


def test_blank_repo(blank_repo):
    """Test a new `Repo` object is as expected"""
    master = blank_repo.main_branch
    assert master.commits == [master.last_commit]
    assert master.name == blank_repo.MAIN_BRANCH
    assert master.branch_commit is None

    assert master.last_commit is not None
    assert master.last_commit.name is not None
    assert master.last_commit.branch == master
    assert master.last_commit.parents == []


def test_first_commit(repo_with_two_commit):
    """Test a commit can be made to the `Repo`"""
    master, = branches(repo_with_two_commit, [])

    assert len(master.commits) == 2
    assert master.branch_commit is None

    assert master.commits[0] != master.commits[1]
    assert master.commits[1].branch == master
    assert master.commits[1].parents == [master.commits[0]]
    assert master.commits[0].parents == []


def test_100_commits(repo_with_100_commits):
    """Test that names and IDs remain unique over lots of commits"""
    master = repo_with_100_commits.main_branch

    for index, commit in enumerate(master.commits):
        assert commit.branch == master

        if index > 0:
            assert commit.parents == [master.commits[index - 1]]

        for other_commit in master.commits[index + 1 :]:
            assert commit.idx != other_commit.idx
            assert commit.name != other_commit.name


def test_first_branch(repo_with_empty_branch, branch_names):
    """Test that a new branch can be created on the `Repo`"""
    repo = repo_with_empty_branch
    branch_name, *_ = branch_names
    branch_1 = repo.branches[branch_name]

    assert len(repo.branches) == 2
    assert branch_1.branch_commit == repo.main_branch.last_commit
    assert branch_1.name == branch_name


def test_duplicate_branch(blank_repo):
    """Test that it's not possible to create branches with the same name"""
    with pytest.raises(BranchException):
        blank_repo.branch(Repo.MAIN_BRANCH)

    assert len(blank_repo.branches) == 1


def test_first_checkout(repo_with_a_basic_branch, branch_names):
    """Test that it is possible to checkout a branch"""
    repo = repo_with_a_basic_branch
    master, branch_1 = branches(repo, branch_names, num_branches=1)

    assert len(branch_1.commits) == 1
    assert len(master.commits) == 1
    assert branch_1.commits[0].parents == [master.commits[0]]
    assert branch_1.branch_commit == master.commits[0]


def test_multiple_checkouts(repo_with_a_complex_branch, branch_names):
    """Test multiple checkouts of different branches"""
    repo = repo_with_a_complex_branch
    master, branch_1 = branches(repo, branch_names, num_branches=1)

    assert len(master.commits) == 2
    assert len(branch_1.commits) == 3
    assert branch_1.commits[2].parents == [branch_1.commits[1]]
    assert branch_1.commits[1].parents == [branch_1.commits[0]]
    assert branch_1.commits[0].parents == [master.commits[0]]
    assert master.commits[1].parents == [master.commits[0]]


def test_failed_checkout(blank_repo):
    """Test checkout of a non-existent branch fails"""
    with pytest.raises(BranchException):
        blank_repo.checkout("bad/branch")


def test_first_merge(repo_with_a_merge, branch_names):
    """Test that branches can be merged"""
    master, branch_1 = branches(repo_with_a_merge, branch_names, num_branches=1)
    merge_commit = master.last_commit

    assert len(master.commits) == 2
    assert len(branch_1.commits) == 1
    assert merge_commit.parents == [master.commits[0], branch_1.commits[0]]


def test_dupe_merge(blank_repo):
    """Test that a branch can't be merged with itself"""
    with pytest.raises(BranchException):
        blank_repo.merge("master")


def test_empty_branch(blank_repo):
    """Test that an empty branch can't be merged but a populated one can"""
    blank_repo.branch("test/branch")
    with pytest.raises(BranchException):
        blank_repo.merge("test/branch")

    blank_repo.checkout("test/branch")
    blank_repo.commit()
    blank_repo.checkout("master")
    blank_repo.merge("test/branch")


def test_repo_with_multiple_merges(repo_with_multiple_merges, branch_names):
    _validate_repos(repo_with_multiple_merges, branch_names, 1, [3, 3], [2, 0])


def test_repo_main_branch_merged_into_other_branch(
    repo_main_branch_merged_into_other_branch, branch_names
):
    _validate_repos(
        repo_main_branch_merged_into_other_branch, branch_names, 1, [4, 3], [1, 1]
    )


def test_repo_with_multiple_branches(repo_with_multiple_branches, branch_names):
    _validate_repos(repo_with_multiple_branches, branch_names, 2, [5, 2, 2], [2, 0, 0])


def test_repo_with_branch_off_branch(repo_with_branch_off_branch, branch_names):
    _validate_repos(repo_with_branch_off_branch, branch_names, 2, [5, 2, 2], [2, 0, 0])

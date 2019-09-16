# -*- coding: utf-8 -*-
"""Testing of the `Repo` object"""
import pytest
from .context import Repo, BranchException


@pytest.fixture
def repo():
    return Repo()


@pytest.fixture
def master(repo):
    return repo.branches[Repo.MAIN_BRANCH]


def test_blank_repo(repo, master):
    """Test a new `Repo` object is as expected"""
    assert master.commits == [master.last_commit]
    assert master.name == repo.MAIN_BRANCH
    assert master.branch_commit is None

    assert master.last_commit is not None
    assert master.last_commit.name is not None
    assert master.last_commit.branch == master
    assert master.last_commit.parents == []


def test_first_commit(repo, master):
    """Test a commit can be made to the `Repo`"""
    initial_commit = master.last_commit
    first_commit = repo.commit()

    assert master.commits == [initial_commit, first_commit]
    assert master.branch_commit is None
    assert master.last_commit == first_commit

    assert first_commit.branch.name == repo.MAIN_BRANCH
    assert first_commit.parents == [initial_commit]


def test_two_commits(repo, master):
    """Test more than one commit can be made to the `Repo`"""
    initial_commit = master.last_commit
    commit_a = repo.commit()
    commit_b = repo.commit()

    assert master.commits == [initial_commit, commit_a, commit_b]
    assert commit_a.parents == [initial_commit]
    assert commit_b.parents == [commit_a]


def test_100_commits(repo):
    """Test that names and IDs remain unique over lots of commits"""
    commits = [repo.commit() for _ in range(100)]
    for ii, commit in enumerate(commits):
        for other_commit in commits[ii + 1 :]:
            assert commit.idx != other_commit.idx
            assert commit.name != other_commit.name


def test_first_branch(repo, master):
    """Test that a new branch can be created on the `Repo`"""
    branch_1 = repo.branch("test/branch")

    assert len(repo.branches) == 2
    assert branch_1.branch_commit == master.last_commit
    assert branch_1.name == "test/branch"
    assert repo.branches["test/branch"] == branch_1


def test_duplicate_branch(repo):
    """Test that it's not possible to create branches with the same name"""
    with pytest.raises(BranchException):
        repo.branch(Repo.MAIN_BRANCH)

    assert len(repo.branches) == 1


def test_first_checkout(repo):
    """Test that it is possible to checkout a branch"""
    branch_1 = repo.branch("test/branch")
    repo.checkout("test/branch")
    new_commit = repo.commit()

    assert new_commit.branch == branch_1
    assert new_commit.parents == [branch_1.branch_commit]


def test_multiple_checkouts(repo, master):
    """Test multiple checkouts of different branches"""
    commit_m1 = master.last_commit
    branch1 = repo.branch("test/branch")
    commit_m2 = repo.commit()
    repo.checkout("test/branch")
    commit_t1 = repo.commit()
    repo.checkout("master")
    commit_m3 = repo.commit()
    repo.checkout("test/branch")
    commit_t2 = repo.commit()

    assert all(c.branch == branch1 for c in [commit_t1, commit_t2])
    assert all(c.branch == master for c in [commit_m2, commit_m3])
    assert commit_t2.parents == [commit_t1]
    assert commit_t1.parents == [commit_m1]
    assert commit_m3.parents == [commit_m2]
    assert commit_m2.parents == [commit_m1]


def test_failed_checkout(repo):
    """Test checkout of a non-existent branch fails"""
    with pytest.raises(BranchException):
        repo.checkout("bad/branch")


def test_first_merge(repo, master):
    """Test that branches can be merged"""
    first_commit = master.last_commit
    repo.branch("test/branch")
    repo.checkout("test/branch")
    new_commit = repo.commit()
    repo.checkout("master")
    repo.merge("test/branch")
    merge_commit = master.last_commit

    assert merge_commit.parents == [first_commit, new_commit]
    assert merge_commit.branch == master


def test_dupe_merge(repo):
    """Test that a branch can't be merged with itself"""
    with pytest.raises(BranchException):
        repo.merge("master")


def test_empty_branch(repo):
    """Test that an empty branch can't be merged but a populated one can"""
    repo.branch("test/branch")
    with pytest.raises(BranchException):
        repo.merge("test/branch")

    repo.checkout("test/branch")
    repo.commit()
    repo.checkout("master")
    repo.merge("test/branch")

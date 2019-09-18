# -*- coding: utf-8 -*-
"""Common fixtures for tests"""
import pytest
from .context import Repo


@pytest.fixture
def blank_repo():
    """An blank git repo with just one commit"""
    return Repo()


@pytest.fixture
def branch_names():
    """A list of names used for branches"""
    return ["branch/1", "branch/2"]


@pytest.fixture
def repo_with_two_commit(blank_repo):
    """A git repo containing two commits

    Repo: x-x-
    """
    blank_repo.commit()
    return blank_repo


@pytest.fixture
def repo_with_100_commits(blank_repo):
    """A git repo containing 100 commits

    Repo: x-x-x-- ... -x-x
    """
    [blank_repo.commit() for _ in range(100)]
    return blank_repo


@pytest.fixture
def repo_with_empty_branch(blank_repo, branch_names):
    """A git repo with an empty branch

    Repo: x-
           \
    """
    branch_name, *_ = branch_names
    blank_repo.branch(branch_name)
    return blank_repo


@pytest.fixture
def repo_with_a_basic_branch(blank_repo, branch_names):
    """A git repo with a basic branch

    Repo: x---
           \
            x-
    """
    branch_1, *_ = branch_names
    blank_repo.branch(branch_1)
    blank_repo.checkout(branch_1)
    blank_repo.commit()
    return blank_repo


@pytest.fixture
def repo_with_a_complex_branch(blank_repo, branch_names):
    """A git repo with a complex branch

    Repo: x-----x--
           \
            x-x---x
    """
    branch_1, *_ = branch_names
    blank_repo.branch(branch_1)
    blank_repo.checkout(branch_1)
    blank_repo.commit()
    blank_repo.commit()
    blank_repo.checkout(blank_repo.MAIN_BRANCH)
    blank_repo.commit()
    blank_repo.checkout(branch_1)
    blank_repo.commit()
    return blank_repo


@pytest.fixture
def repo_with_a_merge(blank_repo, branch_names):
    """A git repo containing a merge

    Repo: x---x
           \ /
            x
    """
    branch_1, *_ = branch_names
    blank_repo.branch(branch_1)
    blank_repo.checkout(branch_1)
    blank_repo.commit()
    blank_repo.checkout(blank_repo.MAIN_BRANCH)
    blank_repo.merge(branch_1)
    return blank_repo


@pytest.fixture
def repo_with_multiple_merges(blank_repo, branch_names):
    """A git repo containing multiple merges

    Repo: x---x-----x
           \ /     /
            x---x-x
    """
    branch_1, *_ = branch_names
    blank_repo.branch(branch_1)
    blank_repo.checkout(branch_1)
    blank_repo.commit()
    blank_repo.checkout(blank_repo.MAIN_BRANCH)
    blank_repo.merge(branch_1)
    blank_repo.checkout(branch_1)
    blank_repo.commit()
    blank_repo.commit()
    blank_repo.checkout(blank_repo.MAIN_BRANCH)
    blank_repo.merge(branch_1)
    return blank_repo


@pytest.fixture
def repo_main_branch_merged_into_other_branch(blank_repo, branch_names):
    """A git repo with a forward merge

    Repo: x---x-x-----x
           \     \   /
            x-----x-x
    """
    branch_1, *_ = branch_names
    blank_repo.branch(branch_1)
    blank_repo.checkout(branch_1)
    blank_repo.commit()
    blank_repo.checkout(blank_repo.MAIN_BRANCH)
    blank_repo.commit()
    blank_repo.commit()
    blank_repo.checkout(branch_1)
    blank_repo.merge(blank_repo.MAIN_BRANCH)
    blank_repo.commit()
    blank_repo.checkout(blank_repo.MAIN_BRANCH)
    blank_repo.merge(branch_1)
    return blank_repo


@pytest.fixture
def repo_with_multiple_branches(blank_repo, branch_names):
    """A git repo with two branches off the main branch

    Repo: x---x------x-x--x
           \   \   /     /
            x---\-x     /
                 \     /
                  x---x
    """
    branch_1, branch_2, *_ = branch_names
    blank_repo.branch(branch_1)
    blank_repo.checkout(branch_1)
    blank_repo.commit()
    blank_repo.checkout(blank_repo.MAIN_BRANCH)
    blank_repo.commit()
    blank_repo.branch(branch_2)
    blank_repo.checkout(branch_2)
    blank_repo.commit()
    blank_repo.checkout(branch_1)
    blank_repo.commit()
    blank_repo.checkout(blank_repo.MAIN_BRANCH)
    blank_repo.merge(branch_1)
    blank_repo.commit()
    blank_repo.checkout(branch_2)
    blank_repo.commit()
    blank_repo.checkout(blank_repo.MAIN_BRANCH)
    blank_repo.merge(branch_2)
    return blank_repo


@pytest.fixture
def repo_with_branch_off_branch(blank_repo, branch_names):
    """A git repo a branch off of a branch

    Repo: x---------x-x-x-x
           \         /   /
            x-x-----/----
               \   /
                x-x
    """
    branch_1, branch_2, *_ = branch_names
    blank_repo.branch(branch_1)
    blank_repo.checkout(branch_1)
    blank_repo.commit()
    blank_repo.commit()
    blank_repo.branch(branch_2)
    blank_repo.checkout(branch_2)
    blank_repo.commit()
    blank_repo.commit()
    blank_repo.checkout(blank_repo.MAIN_BRANCH)
    blank_repo.commit()
    blank_repo.merge(branch_2)
    blank_repo.commit()
    blank_repo.merge(branch_1)
    return blank_repo

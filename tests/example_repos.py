# -*- coding: utf-8 -*-
# pylint: disable=W1401
"""Example repos for use in testing"""
from .context import Repo


def hundred_commits():
    """A git repo containing 100 commits

    Repo: x-x-x-- ... -x-x
    """
    repo = Repo()
    for _ in range(100):
        repo.commit()
    return repo


def branch_with_commits(branch_name):
    """A git repo with a long branch

    Repo: x-----x--
           \
            x-x---x

    :param branch_name: The name of the branch
    """
    repo = Repo()
    repo.branch(branch_name)
    repo.branch(branch_name)
    repo.checkout(branch_name)
    repo.commit()
    repo.commit()
    repo.checkout(Repo.MAIN_BRANCH)
    repo.commit()
    repo.checkout(branch_name)
    repo.commit()
    return repo


def multiple_merges(branch_name):
    """A git repo containing multiple merges

    Repo: x---x---x
           \ /   /
            x---x

    :param branch_name: The name of the branch
    """
    repo = Repo()
    repo.branch(branch_name)
    repo.checkout(branch_name)
    repo.commit()
    repo.checkout(Repo.MAIN_BRANCH)
    repo.merge(branch_name)
    repo.checkout(branch_name)
    repo.commit()
    repo.checkout(repo.MAIN_BRANCH)
    repo.merge(branch_name)
    return repo


def forward_merge(branch_name):
    """A git repo with a forward merge

    Repo: x---x---x
           \   \ /
            x---x

    :param branch_name: The name of the branch
    """
    repo = Repo()
    repo.branch(branch_name)
    repo.checkout(branch_name)
    repo.commit()
    repo.checkout(Repo.MAIN_BRANCH)
    repo.commit()
    repo.checkout(branch_name)
    repo.merge(Repo.MAIN_BRANCH)
    repo.checkout(Repo.MAIN_BRANCH)
    repo.merge(branch_name)
    return repo


def multiple_branches(branch_names):
    """A git repo with two branches off the main branch

    Repo: x---x----x--x
           \   \  /  /
            x---\-  /
                 \ /
                  x

    :param branch_names: a list of branch names
    """
    branch_1, branch_2 = branch_names
    repo = Repo()
    repo.branch(branch_1)
    repo.checkout(branch_1)
    repo.commit()
    repo.checkout(Repo.MAIN_BRANCH)
    repo.commit()
    repo.branch(branch_2)
    repo.checkout(branch_2)
    repo.commit()
    repo.checkout(Repo.MAIN_BRANCH)
    repo.merge(branch_1)
    repo.merge(branch_2)
    return repo


def branch_off_branch(branch_names):
    """A git repo a branch off of a branch

    Repo: x---x---x
           \ /   /
            x   /
             \ /
              x

    :param branch_names: a list of branch names
    """
    branch_1, branch_2 = branch_names
    repo = Repo()
    repo.branch(branch_1)
    repo.checkout(branch_1)
    repo.commit()
    repo.branch(branch_2)
    repo.checkout(branch_2)
    repo.commit()
    repo.checkout(Repo.MAIN_BRANCH)
    repo.merge(branch_1)
    repo.merge(branch_2)
    return repo


def merge_into_empty_branch(branch_names):
    """A git repo with a merge into an empty branch

    Repo: x----
           \
           |--x
           \ /
            x

    :param branch_names: a list of branch names
    """
    branch_1, branch_2 = branch_names
    repo = Repo()
    repo.branch(branch_1)
    repo.branch(branch_2)
    repo.checkout(branch_2)
    repo.commit()
    repo.checkout(branch_1)
    repo.merge(branch_2)
    return repo

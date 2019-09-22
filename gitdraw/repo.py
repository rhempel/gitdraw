# -*- coding: utf-8 -*-
"""A basic representation of a git repository

Take a basic set of git commands and construct
a lightweight reprenetation of the corresponding
repository
"""
from string import ascii_uppercase
from dataclasses import dataclass
from typing import Any, List, Generator


def _name_gen() -> Generator[str, None, None]:
    """Generate a unique name: A, B, .., AA, AB, .., BA, .."""
    prefix = ""
    names = _name_gen()
    while True:
        for char in ascii_uppercase:
            yield f"{prefix}{char}"
        prefix = next(names)  # pylint: disable=R1708


def _idx_gen() -> Generator[int, None, None]:
    """Generate an infinite list of integers"""
    i = 0
    while True:
        yield i
        i += 1


class BranchException(Exception):
    """Raised for issues associated with `Branch`"""


class CommitException(Exception):
    """Raised for issues associated with `Commits`"""


@dataclass
class Commit:
    """A git commit object"""

    name: str
    idx: int
    message: str
    parents: List[Any]
    branch: Any


@dataclass
class MergeCommit(Commit):
    """A git commit that resulted from a merge"""

    @property
    def merge_commit(self):
        """The last commit in the branch that was merged"""
        return next(c for c in self.parents if c.branch == self._from_branch)

    @property
    def _from_branch(self):
        """The branch that was merged"""
        from_commits = [fc for fc in self.parents if fc.branch != self.branch]
        if len(from_commits) == 1:
            return from_commits[0].branch

        for commit in from_commits:
            if commit.branch != self.branch.branch_commit.branch:
                branch = commit.branch
                break
        else:
            raise RuntimeError("Unexpected error occurred")

        return branch


@dataclass
class Branch:
    """A git branch object"""

    name: str
    idx: int
    branch_commit: Any
    commits: List[Any]

    @property
    def last_commit(self) -> Commit:
        """The latest commit on this branch"""
        if not self.commits:
            return self.branch_commit
        return self.commits[-1]

    @property
    def can_merge(self) -> bool:
        """If the branch can be merged into another branch"""
        return len(self.commits) > 0


class Repo:
    """An object representing a git repository.

    Supports the following git commands:
    * checkout
    * commit
    * merge
    * branch
    """

    MAIN_BRANCH = "master"

    def __init__(self):
        self.branches = {}
        self._commit_name = _name_gen()
        self._commit_idx = _idx_gen()
        self._branch_idx = _idx_gen()
        self._active_branch = None
        self._init_main_branch()

    def _init_main_branch(self):
        """Add a master branch with a commit to the repo"""
        self._branch(self.MAIN_BRANCH, first=True)
        self.checkout(self.MAIN_BRANCH)
        self.commit(message="intial commit")

    def _branch_from_name(self, name) -> Branch:
        """Find a `Branch` given it's name

        :param name: The name of the `Branch` to find
        :raises BranchException: If the `Branch` doesn't exist
        """
        try:
            return self.branches[name]
        except KeyError:
            raise BranchException(f"No branch named {name}")

    @property
    def main_branch(self):
        """Return the main branch"""
        return self._branch_from_name(self.MAIN_BRANCH)

    def checkout(self, branch_name: str):
        """Checkout a `Branch` that exists in the `Repo`

        :param branch_name: The name of the `Branch` to checkout
        """
        self._active_branch = self._branch_from_name(branch_name)

    def branch(self, name: str) -> Branch:
        """Create a new `Branch` in the `Repo`

        Branch off from the last commit on the currently active branch.

        :param name: The name of the `Branch` to add
        """
        return self._branch(name, first=False)

    def _branch(self, name: str, first: bool) -> Branch:
        """Add a `Branch to the `Repo`

        :param name: The name of the `Branch` to add
        :param first: set to True if this is the first `Branch` in
            the repo (the first branch has no parents)
        """
        if name in self.branches:
            raise BranchException(f"Branch exists {self._branch_from_name(name)}")
        branch_commit = None if first else self._active_branch.commits[-1]
        self.branches[name] = Branch(name, next(self._branch_idx), branch_commit, [])
        return self._branch_from_name(name)

    def commit(self, message=None) -> Commit:
        """Make a commit on the currently active `Branch`

        :param message: Add a message to the commit (currently unused)
        """
        message = "" if message is None else message
        parent = self._active_branch.last_commit
        parents = [] if parent is None else [parent]
        commit = Commit(
            next(self._commit_name),
            next(self._commit_idx),
            message,
            parents,
            self._active_branch,
        )
        self._active_branch.commits.append(commit)
        return commit

    def merge(self, branch_name: str):
        """Merge a `Branch` into the currently active `Bracnh`

        :param branch_name: The name of the `Branch` to merge`
        """
        branch = self._branch_from_name(branch_name)
        if branch == self._active_branch:
            raise BranchException(f"Cannot merge into self")
        if not branch.can_merge:
            raise BranchException(f"Branch cannot be merged")
        if branch.last_commit in self._active_branch.last_commit.parents:
            raise BranchException(f"Branch already merged")

        commit = MergeCommit(
            next(self._commit_name),
            next(self._commit_idx),
            f"Merge {branch.name} -> {self._active_branch.name}",
            [self._active_branch.last_commit, branch.last_commit],
            self._active_branch,
        )
        self._active_branch.commits.append(commit)

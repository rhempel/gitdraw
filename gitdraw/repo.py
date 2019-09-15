from string import ascii_uppercase
from dataclasses import dataclass
from typing import Any, List, Generator


def _name_gen() -> Generator[str, None, None]:
    prefix = ""
    while True:
        for char in ascii_uppercase:
            yield f"{prefix}{char}"
        prefix = next(_name_gen())


def _idx_gen() -> Generator[int, None, None]:
    i = 0
    while True:
        yield i
        i += 1


class BranchException(Exception):
    pass


@dataclass
class Commit:
    name: str
    idx: int
    message: str
    parents: List[Any]
    branch: Any


@dataclass
class Branch:
    name: str
    idx: int
    branch_commit: Any
    commits: List[Any]

    @property
    def last_commit(self) -> Commit:
        if not self.commits:
            return self.branch_commit
        return self.commits[-1]

    @property
    def can_merge(self) -> bool:
        return len(self.commits) > 0


class Repo:
    MAIN_BRANCH = "master"

    def __init__(self):
        self.branches = {}
        self._commit_name = _name_gen()
        self._commit_idx = _idx_gen()
        self._branch_idx = _idx_gen()
        self._active_branch = None
        self._init_main_branch()

    def _init_main_branch(self):
        self._branch(self.MAIN_BRANCH, first=True)
        self.checkout(self.MAIN_BRANCH)
        self.commit(message="intial commit")

    def _branch_from_name(self, name) -> Branch:
        try:
            return self.branches[name]
        except KeyError:
            raise BranchException(f"No branch named {name}")

    def checkout(self, branch_name: str):
        self._active_branch = self._branch_from_name(branch_name)

    def branch(self, name: str) -> Branch:
        return self._branch(name, first=False)

    def _branch(self, name: str, first: bool) -> Branch:
        if name in self.branches:
            raise BranchException(f"Branch exists {self._branch_from_name(name)}")
        branch_commit = None if first else self._active_branch.commits[-1]
        self.branches[name] = Branch(name, next(self._branch_idx), branch_commit, [])
        return self._branch_from_name(name)

    def commit(self, message=None) -> Commit:
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
        branch = self._branch_from_name(branch_name)
        if branch == self._active_branch:
            raise BranchException(f"Cannot merge into self")
        if not branch.can_merge:
            raise BranchException(f"Branch cannot be merged")
        commit = Commit(
            next(self._commit_name),
            next(self._commit_idx),
            f"Merge {branch.name} -> {self._active_branch.name}",
            [self._active_branch.last_commit, branch.last_commit],
            self._active_branch,
        )
        self._active_branch.commits.append(commit)

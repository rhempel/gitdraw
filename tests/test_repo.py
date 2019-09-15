import pytest
from repo import Repo, BranchException


@pytest.fixture
def repo():
    return Repo()


@pytest.fixture
def master(repo):
    return repo.branches[repo.MAIN_BRANCH]


def test_blank_repo(repo, master):
    assert master.commits == [master.last_commit]
    assert master.name == repo.MAIN_BRANCH
    assert master.branch_commit is None

    assert master.last_commit is not None
    assert master.last_commit.name is not None
    assert master.last_commit.branch == master
    assert master.last_commit.parents == []


def test_first_commit(repo, master):
    initial_commit = master.last_commit
    first_commit = repo.commit()

    assert master.commits == [initial_commit, first_commit]
    assert master.branch_commit is None
    assert master.last_commit == first_commit

    assert first_commit.branch.name == repo.MAIN_BRANCH
    assert first_commit.parents == [initial_commit]


def test_two_commits(repo, master):
    initial_commit = master.last_commit
    commit_a = repo.commit()
    commit_b = repo.commit()

    assert master.commits == [initial_commit, commit_a, commit_b]
    assert commit_a.parents == [initial_commit]
    assert commit_b.parents == [commit_a]


def test_first_branch(repo, master):
    branch_1 = repo.branch("test/branch")

    assert len(repo.branches) == 2
    assert branch_1.branch_commit == master.last_commit
    assert branch_1.name == "test/branch"
    assert repo.branches["test/branch"] == branch_1


def test_duplicate_branch(repo, master):
    with pytest.raises(BranchException):
        repo.branch(repo.MAIN_BRANCH)

    assert len(repo.branches) == 1


def test_first_checkout(repo, )
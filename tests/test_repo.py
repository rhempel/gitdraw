import pytest
from .context import Repo, BranchException


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


def test_100_commits(repo):
    [repo.commit() for _ in range(100)]


def test_first_branch(repo, master):
    branch_1 = repo.branch("test/branch")

    assert len(repo.branches) == 2
    assert branch_1.branch_commit == master.last_commit
    assert branch_1.name == "test/branch"
    assert repo.branches["test/branch"] == branch_1


def test_duplicate_branch(repo):
    with pytest.raises(BranchException):
        repo.branch(repo.MAIN_BRANCH)

    assert len(repo.branches) == 1


def test_first_checkout(repo):
    branch_1 = repo.branch("test/branch")
    repo.checkout("test/branch")
    new_commit = repo.commit()

    assert new_commit.branch == branch_1
    assert new_commit.parents == [branch_1.branch_commit]


def test_multiple_checkouts(repo, master):
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
    with pytest.raises(BranchException):
        repo.checkout("bad/branch")


def test_first_merge(repo, master):
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
    with pytest.raises(BranchException):
        repo.merge("master")

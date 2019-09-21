# -*- coding: utf-8 -*-
# pylint: disable=W0621
"""Test parsing of git commands"""
import pytest
import os
import uuid
from unittest.mock import Mock
from tempfile import NamedTemporaryFile
from tests.context import parse_string, parse_file, GitParseError, InvalidGitCmd, Repo


@pytest.mark.parametrize(
    "git_string,git_func,args",
    [
        ("git commit", "commit", None),
        ('git commit -m "a message"', "commit", ("a message",)),
        ("git branch my/branch", "branch", ("my/branch",)),
        ("git checkout new/branch", "checkout", ("new/branch",)),
        ("git merge new/feature", "merge", ("new/feature",)),
    ],
)
def test_basic_commands(git_string, git_func, args):
    repo = Mock(spec=Repo)
    # setattr(repo, git_func, MagicMock())
    parse_string(git_string, repo)
    if args:
        getattr(repo, git_func).assert_called_once_with(*args)
    else:
        getattr(repo, git_func).assert_called_once()


def test_parse_error():
    repo = Mock(spec=Repo)
    with pytest.raises(GitParseError) as e:
        parse_string("garbage", repo)
        assert "garbage" in str(e)


def test_invalid_git():
    repo = Repo()
    with pytest.raises(InvalidGitCmd) as e:
        parse_string("git checkout made/up", repo)
        assert "BranchException" in str(e)


def test_from_file():
    test_string = "\n".join(["git commit", "git branch new/branch"])
    repo = Mock(spec=Repo)
    filename = str(uuid.uuid4())
    try:
        with open(filename, "w") as f:
            f.write(test_string)

        # TODO fix this up
        parse_string(test_string, repo)
        # parse_file(filename, repo)
    finally:
        os.remove(filename)
    print("test")

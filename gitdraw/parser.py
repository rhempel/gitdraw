# -*- coding: utf-8 -*-
"""Parsing of git commands"""
import logging
from parsimonious.grammar import Grammar  # type: ignore
from parsimonious.nodes import NodeVisitor  # type: ignore
from parsimonious.exceptions import ParseError, VisitationError  # type: ignore
from gitdraw.repo import Repo

LOG = logging.getLogger(__name__)


class GitParseError(ParseError):
    """Error raised when we can't parse a file"""

    def __str__(self):
        start_pos = self.text[: self.pos].rfind("\n")
        if start_pos != 0:
            start_pos += 1

        end_pos = self.text[self.pos :].find("\n")
        if end_pos != -1:
            end_pos += self.pos

        return u"Error [line %s, column %s]: '%s'" % (
            self.line(),
            self.column(),
            self.text[start_pos:end_pos],
        )

    @classmethod
    def from_error(cls, error: ParseError):
        """Create from a `ParseError`"""
        return cls(error.text, error.pos, error.expr)


class InvalidGitCmd(Exception):
    """Error raised when a git command is invalid"""

    def __init__(self, message):
        """Make the error more obvious"""
        message = message.split("\n")[0]
        super(InvalidGitCmd, self).__init__(message)

    @classmethod
    def from_error(cls, error: VisitationError):
        """Create from a `ParseError`"""
        return cls(str(error))


GRAMMAR = Grammar(
    """
    cmds     = gitcmd*
    gitcmd   = git cmd ws?
    git      = "git "
    cmd      = ckt / brch / cmt / mrg
    ckt      = "checkout " name
    brch     = "branch "  name
    cmt      = "commit" cmt_rgz?
    mrg      = "merge " name
    cmt_rgz  = " -m \\"" msg "\\""
    msg      = ~"[^\\"]*"
    name     = ~"[a-zA-Z0-9\\/-_]*[a-zA-Z0-9]"
    ws       = ~"\\s*"
    """
)


class GitVisitor(NodeVisitor):
    """Execute commands in a git repo based on text input"""

    def __init__(self, repo: Repo, *args, **kwargs):
        super(GitVisitor, self).__init__(*args, **kwargs)
        self.repo = repo

    def visit_ckt(self, _, visited_children):
        """Perform the git checkout"""
        branch_name = visited_children[-1]
        LOG.debug("Checkout %s.", branch_name)
        self.repo.checkout(branch_name)

    def visit_cmt(self, _, visited_children):
        """Perform the git commit"""
        if isinstance(visited_children[-1], list):
            message = visited_children[-1][0]
            LOG.debug("Commit %s.", message)
            self.repo.commit(message)
        else:
            LOG.debug("Commit.")
            self.repo.commit()

    def visit_brch(self, _, visited_children):
        """Returns the overall output."""
        branch_name = visited_children[-1]
        LOG.debug("Branch %s.", branch_name)
        self.repo.branch(branch_name)

    def visit_mrg(self, _, visited_children):
        """Perform the git merge"""
        branch_name = visited_children[-1]
        LOG.debug("Merge %s.", branch_name)
        self.repo.merge(branch_name)

    def visit_name(self, node, _):  # pylint: disable=R0201
        """Return the branch name"""
        LOG.debug("branch name: %s", node.text)
        return node.text

    def visit_cmt_rgz(self, _, visited_children):  # pylint: disable=R0201
        """Extract and return the commit merge"""
        _, msg, _ = visited_children
        LOG.debug("commit message: %s", msg)
        return msg

    def visit_msg(self, node, _):  # pylint: disable=R0201
        """Return the message"""
        return node.text

    def generic_visit(self, node, visited_children):
        """The generic visit method."""
        return visited_children or node


def parse_file(file_path: str, repo: Repo) -> Repo:
    """Extract git commands from a file and run using a `Repo`

    :param file_path: The path to the file to read
    :param repo: The `Repo` to use
    :raises GitParseError: The contents of the file was invalid
    :raises InvalidGitCmd: The git command issued was invalid
    """
    with open(file_path, "r") as my_file:
        text = "\n".join(my_file.readlines())

    return parse_string(text, repo)


def parse_string(git_commands: str, repo: Repo) -> Repo:
    """Parse git commands and run using a `Repo`

    :param git_commands: a newline seperated list of git commands
    :param repo: The `Repo` to use
    """
    visitor = GitVisitor(repo)
    try:
        tree = GRAMMAR.parse(git_commands)
    except ParseError as exception:
        raise GitParseError.from_error(exception)

    try:
        visitor.visit(tree)
    except VisitationError as exception:
        raise InvalidGitCmd.from_error(exception)

    return visitor.repo

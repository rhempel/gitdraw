#!/uar/bin/python3.7
# -*- coding: utf-8 -*-
"""Prototype script that creates an SVG image of a git `Repo`"""
import argparse
from gitdraw import (
    parse_file,
    GitParseError,
    InvalidGitCmd,
    Drawer,
    SvgDrawingTool,
    Repo,
)

FAILED_PARSE = 3
BAD_COMMANDS = 4


def get_parser() -> argparse.ArgumentParser:
    """The command line parser"""
    parser = argparse.ArgumentParser(description="GitDraw")
    parser.add_argument("-o", "--output", help="Output file name", default="stdout")
    parser.add_argument(
        "-d", "--darkmode", action="store_true", help="Render in dark mode"
    )

    required_named = parser.add_argument_group("required named arguments")
    required_named.add_argument("-i", "--input", help="Input file name", required=True)
    return parser


def main() -> int:
    """Main program path"""
    parser = get_parser()
    args = parser.parse_args()

    try:
        repo = parse_file(args.input, Repo())
    except GitParseError as exception:
        print(exception)
        return FAILED_PARSE
    except InvalidGitCmd as exception:
        print(exception)
        return BAD_COMMANDS

    drawer = Drawer(dark_mode=args.darkmode)
    output = drawer.draw_repo(repo, SvgDrawingTool())

    if args.output == "stdout":
        print(output)
    else:
        with open(args.output, "w") as outfile:
            outfile.write(output)

    return 0


if __name__ == "__main__":
    exit(main())

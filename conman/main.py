from __future__ import annotations

import argparse
import logging
import os
import sys
from typing import Any
from typing import Optional
from typing import Sequence
from typing import Union
import conman.constants as C

from conman.commands.init import init
from conman.commands.clean import clean
from conman.commands.status import status
from conman.commands.build import build
from conman.commands.update import update


CMDS = {
    "init": {"func": init, "kargs": ["force", "optional"]},
    "clean": {"func": clean, "kargs": []},
    "status": {"func": status, "kargs": []},
    "build": {"func": build, "kargs": []},
    "update": {"func": update, "kargs": []},
}


def main(argv: Optional[Sequence[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(
        prog="conman",
        description="Conman is a tool to manage yours containers",
    )

    # https://stackoverflow.com/a/8521644/812183
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {C.VERSION}",
    )

    # Generic options - Options group
    # group = parser.add_mutually_exclusive_group()
    # ## Working directory
    # group.add_argument(
    #     "-f",
    #     "--file",
    #     help="Specify an alternate project file",
    # )
    # ## Verbose
    # group.add_argument(
    #     "-v",
    #     "--verbose",
    #     action="store_true",
    #     help="Increase verbosity",
    # )

    # Subparsers
    subparsers = parser.add_subparsers(dest="command")

    # Main commands - Subparsers

    ## Status command
    status_impl_parser = subparsers.add_parser(
        "status", help="Show the project status (not implemented yet)"
    )

    ## Init command
    init_impl_parser = subparsers.add_parser(
        "init", help="Initialize a new project"
    )
    init_impl_parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force initialization, even if the project already exists",
    )

    init_impl_parser.add_argument(
        "--optional",
        "-opt",
        action="store_true",
        help="Add more options to the conman config file",
    )

    ## Install command
    build_impl_parser = subparsers.add_parser("build", help="Build project")
    
    ## Update command
    update_impl_parser = subparsers.add_parser("update", help="Update project")

    ## Clean command
    clean_impl_parser = subparsers.add_parser("clean", help="Clean project")

    # Analyse command line arguments
    args = parser.parse_args(argv)

    # # Update commands attributes relatives to options
    # ## Working directory
    # if args.file:
    #     if os.path.exists(os.path.dirname(args.file)):
    #         pass
    #     else:
    #         print(
    #             f"Specified directory: {os.path.dirname(args.file)} do not exist."
    #         )
    # if args.verbose:
    #     status()

    # Run the command
    extra_args = {}
    for key, value in CMDS.items():
        if args.command == key:
            for kwarg in value["kargs"]:
                if hasattr(args, kwarg):
                    extra_args.update({kwarg: getattr(args, kwarg)})
            value["func"](**extra_args)

    # return 0


if __name__ == "__main__":
    raise SystemExit(main())

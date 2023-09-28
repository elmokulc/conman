from __future__ import annotations

from conman import utils
from conman.constants import CONFIG_FILE
from conman.commands.build import Config
import os


def init(force=False) -> int:
    if not force:
        print("Initializing conman project")
        # Check if .conman-config.yml already exists in current directory
        if os.path.isfile(".conman-config.yml"):
            print(
                "Warning : .conman-config.yml already exists in current directory"
            )
            print(
                "Run : 'conman clean' to remove it first or 'conman init --force (or -f)' to overwrite it"
            )
        else:
            Config().dump_conman_config_file(filename=CONFIG_FILE)
        return 0
    else:
        print("Forced Mode - Reinitializing conman project")
        Config().dump_conman_config_file(filename=CONFIG_FILE)
        return 0


if __name__ == "__main__":
    init()

from __future__ import annotations

from conman import utils
from conman.constants import CONFIG_FILE
from conman.commands.build import Config
import os


def init() -> int:
    # Check if .conman-config.yml already exists in current directory
    if os.path.isfile(".conman-config.yml"):
        print(
            "Warning : .conman-config.yml already exists in current directory"
        )
        print(
            "Run : 'conman clean' to remove it first or 'conman init --force' to overwrite it"
        )
    else:
        Config().dump_conman_config_file(filename=CONFIG_FILE)
    return 0


if __name__ == "__main__":
    init()

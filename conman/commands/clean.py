from __future__ import annotations
import os


def clean() -> int:
    # Remove .conman-config.yml file if exists in current directory
    if os.path.isfile(".conman-config.yml"):
        os.remove(".conman-config.yml")
        print("Config file removed")
    return 0

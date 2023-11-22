from __future__ import annotations
import importlib.metadata


CONFIG_DIRNAME = ".conman"
CONFIG_DIR = f"./{CONFIG_DIRNAME}/"
CONFIG_FILE = CONFIG_DIR + "conman-config.yml"

VERSION = importlib.metadata.version("conman-tool")

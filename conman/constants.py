from __future__ import annotations
import importlib.metadata

CONFIG_DIR = "./.conman/"
CONFIG_FILE = CONFIG_DIR + "conman-config.yml"

VERSION = importlib.metadata.version("conman-tool")

from __future__ import annotations
import os
from conman.constants import *
from conman.commands.build import Config
import shutil


def clean() -> int:

    config = Config().load_conman_config_file(filename=CONFIG_FILE)

    if (
        config.images.root.generate
        and config.images.root.conda_environment is not None
    ):
        print("Deleteting conda environment file")
        conda_env_file = config.images.root.conda_environment.environment_file
        os.remove(f"{conda_env_file}")

    if config.container.devcontainer is not None:
        print("Deleteting .devcontainer folder")
        shutil.rmtree("./.devcontainer/")
    else:
        if config.images.root.generate:
            print("Deleteting Dockerfile.root")
            os.remove("./Dockerfile.root")
        print("Deleteting Dockerfile.user")
        os.remove("./Dockerfile.user")
        print("Deleteting docker-compose.yml")
        os.remove("./docker-compose.yml")


if __name__ == "__main__":
    clean()

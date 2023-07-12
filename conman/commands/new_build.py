from __future__ import annotations

from typing import Any, Dict, List, Optional, Union, Protocol
from pathlib import Path

import os


class Conda:
    enabled: bool = True
    directory: Path = "/opt/conda"
    env_name: str = "myenv"
    environment_file: Path = "./environment.yml"

    def manage_conda_env_file(
        envfile,
        conda_env_name,
        pip_packages=["scipy", "opencv-python", "opencv-contrib-python"],
        conda_packages=["python=3.8", "pip", "numpy"],
        channels=["conda-forge", "anaconda", "defaults"],
    ):
        """_summary_
        Manage conda environment.yml file
        if file exists do nothing else create an empty file
        Args:
            envfile (str): environment.yml file path
        """

        if not os.path.isfile(envfile):
            print(f"Creating conda env file at: \t{envfile}")
            open(envfile, "w").write("name: " + conda_env_name + "\n")
            open(envfile, "a").write("channels: \n")
            for channel in channels:
                open(envfile, "a").write("  - " + channel + "\n")
            open(envfile, "a").write("dependencies: \n")
            for conda_package in conda_packages:
                open(envfile, "a").write("  - " + conda_package + "\n")
            open(envfile, "a").write("  - pip: \n")
            for pip_package in pip_packages:
                open(envfile, "a").write("    - " + pip_package + "\n")
        else:
            print(f"Conda env file exists at: \t{envfile}")


class Image:
    name: str
    tag: str
    from_image: Dict[str, str] = {"name": "ubuntu", "tag": "20.04"}
    extra_instructions: List[str] = []

    def to_dockerfile(self, filename: str = "Dockerfile") -> str:
        ...


class Graphical:
    enabled: bool = False
    protocol: str = "x11"

    def x_access() -> None:
        # Give access to X11
        print("Executing xhost +local: ...")
        os.system("xhost +local:")


class Gpu:
    enabled: bool = False
    manufacturer: str = "nvidia"
    count: int = 1


class Build:
    args: List[str] = []
    context: Path = Path(".")
    dockerfile: Path = Path("./Dockerfile-user")


class Resources:
    limits: Dict[str, str or int] = {}
    reservations: Dict[Dict[List[Dict]]] = {
        "devices": [
            {"driver": Gpu.manufacturer},
            {"count": Gpu.count},
            {"capabilities": list("gpu")},
        ]
    }


class Deploy:
    resources: Resources


class Service:
    name: str
    ports: List[int] = []
    volumes: List[Path] = []
    privileged: bool = False
    network_mode: str = "host"
    build: Build
    deploy: Deploy


class DevContainer:
    enable: bool = False
    name: str = "devcontainer_name"
    extensions: List[str] = []

    def to_devcontainer_json(self, filename="devcontainer.json") -> None:
        ...


class Container:
    name: str
    services: Dict[str, Service] = {f"{Service.name}": Service}
    version: str = "3.9"
    gpu: Gpu
    graphical: Graphical
    devcontainer: DevContainer


class UserSettings:
    volumes: List[str] = []


class Config:
    images: Dict[str, Union[Image, Image]] = {
        "root": Image,
        "user": Image,
    }
    container: Container
    user_settings: UserSettings

    def load_conman_config_file(
        self, filename: Path = ".conman-config.yml"
    ) -> None:
        ...

    def dump_conman_config_file(
        self, filename: Path = ".conman-config.yml"
    ) -> None:
        ...

    def to_docker_compose(
        self, filename: Path = "./docker-compose.yml"
    ) -> None:
        ...

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
        self,
        pip_packages=["scipy", "opencv-python", "opencv-contrib-python"],
        conda_packages=["python=3.8", "pip", "numpy"],
        channels=["conda-forge", "anaconda", "defaults"],
    ) -> None:
        """_summary_
        Manage conda environment.yml file
        if file exists do nothing else create an empty file
        Args:
            self.environment_file (str): environment.yml file path
        """

        if not os.path.isfile(self.environment_file):
            print(f"Creating conda env file at: \t{self.environment_file}")
            open(self.environment_file, "w").write(
                "name: " + self.env_name + "\n"
            )
            open(self.environment_file, "a").write("channels: \n")
            for channel in channels:
                open(self.environment_file, "a").write("  - " + channel + "\n")
            open(self.environment_file, "a").write("dependencies: \n")
            for conda_package in conda_packages:
                open(self.environment_file, "a").write(
                    "  - " + conda_package + "\n"
                )
            open(self.environment_file, "a").write("  - pip: \n")
            for pip_package in pip_packages:
                open(self.environment_file, "a").write(
                    "    - " + pip_package + "\n"
                )
        else:
            print(f"Conda env file exists at: \t{self.environment_file}")


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
    resources: Resources = Resources()


class Service:
    name: str
    ports: List[int] = []
    volumes: List[Path] = []
    privileged: bool = False
    network_mode: str = "host"
    build: Build = Build()
    deploy: Deploy = Deploy()


class Services:
    main_service: Service = Service()

    def add_service(self, service: Service) -> None:
        ...


class Compose:
    version: str = "3.9"
    services: Services = Services()

    def to_docker_compose(
        self, filename: Path = "./docker-compose.yml"
    ) -> None:
        ...


class DevContainer:
    enable: bool = False
    name: str = "devcontainer_name"
    extensions: List[str] = []

    def to_devcontainer_json(self, filename="devcontainer.json") -> None:
        ...


class Container:
    name: str = "container_name"
    gpu: Gpu = Gpu()
    graphical: Graphical = Graphical()
    devcontainer: DevContainer = DevContainer()


class UserSettings:
    volumes: List[str] = []

    def update_volumes(self, volumes: List[str]) -> None:
        ...

    def check_volumes(self, volumes: List[str]) -> None:
        ...


class Config:
    images: Dict[str, Union[Image, Image]] = {
        "root": Image(),
        "user": Image(),
    }
    container: Container = Container()
    user_settings: UserSettings = UserSettings()

    def load_conman_config_file(
        self, filename: Path = ".conman-config.yml"
    ) -> None:
        ...

    def dump_conman_config_file(
        self, filename: Path = ".conman-config.yml"
    ) -> None:
        ...


if __name__ == "__main__":
    config = Config()

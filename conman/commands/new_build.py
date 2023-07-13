from __future__ import annotations

from typing import Any, Dict, List, Optional, Union, Protocol
from pathlib import Path

import os
from conman import utils
import yaml
from dataclasses import dataclass


def asi(subclass):
    """
    A decorator function that adds support for automatic super() initialization to a subclass.

    Args:
        subclass (class): The subclass to decorate.

    Returns:
        class: The decorated subclass.
    """

    original_init = subclass.__init__

    def new_init(self, *args, **kwargs):
        """
        Custom initialization method that automatically calls super().__init__().

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            None
        """

        super(subclass, self).__init__(*args, **kwargs)
        original_init(self, *args, **kwargs)

    subclass.__init__ = new_init
    return subclass


class _Builder:
    @classmethod
    def from_dic(cls, dic):
        kwargs = {}
        flag = False
        for key, value in dic.items():
            if key in CONFIG:
                _class = CONFIG[key]
            else:
                flag = True
                _class = _Builder

            if value.__class__ == dict:
                kwargs[key] = _class.from_dic(value)
            else:
                kwargs[key] = value

        return cls(**kwargs)

    def __init__(self, **kwargs) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)

        self.class_register()

    @staticmethod
    def class_representer(dumper, data):
        """
        A static method used as a custom YAML representer for Field objects.

        Args:
            dumper (yaml.Dumper): The YAML dumper object.
            data (Field): The Field object to represent.

        Returns:
            Any: The YAML representation of the Field object.
        """

        return dumper.represent_dict(data.__dict__)

    @classmethod
    def class_register(cls):
        """
        Registers the field_representer as a representer for the Field class in YAML.

        Returns:
            None
        """

        yaml.add_representer(cls, cls.class_representer)


@asi
class CondaEnvironment(_Builder):
    enabled: bool = True
    directory: Path = "/opt/conda"
    env_name: str = "myenv"
    environment_file: Path = "./environment.yml"

    def generate_environment_file(
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
            with open(self.environment_file, "w") as file:
                file.write("name: " + self.env_name + "\n")

                # channels
                file.write("channels: \n")
                for channel in channels:
                    file.write("  - " + channel + "\n")

                # dependencies
                file.write("dependencies: \n")
                for conda_package in conda_packages:
                    file.write("  - " + conda_package + "\n")

                # pip packages
                file.write("  - pip: \n")
                for pip_package in pip_packages:
                    file.write("    - " + pip_package + "\n")
        else:
            print(f"Conda env file exists at: \t{self.environment_file}")


@asi
class Image(_Builder):
    name: str
    tag: str
    from_image: Dict[str, str] = {"name": "ubuntu", "tag": "20.04"}
    extra_instructions: List[str] = []

    def to_dockerfile(self, filename: str = "Dockerfile") -> str:
        ...


@asi
class Graphical(_Builder):
    enabled: bool = False
    protocol: str = "x11"

    def x_access() -> None:
        # Give access to X11
        print("Executing xhost +local: ...")
        os.system("xhost +local:")


@asi
class Gpu(_Builder):
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


@asi
class DevContainer(_Builder):
    enable: bool = False
    name: str = "devcontainer_name"
    extensions: List[str] = []

    def to_devcontainer_json(self, filename="devcontainer.json") -> None:
        ...


@asi
class Container(_Builder):
    name: str = "container_name"
    gpu: Gpu = Gpu()
    graphical: Graphical = Graphical()
    devcontainer: DevContainer = DevContainer()


@asi
class UserSettings(_Builder):
    volumes: List[str] = ["../:/workspace"]

    def update_volumes(self, volumes: List[str]) -> None:
        ...

    def check_volumes(self, volumes: List[str]) -> None:
        ...


CONFIG = {
    "root": Image,
    "user": Image,
    "user_settings": UserSettings,
    "container": Container,
    "gpu": Gpu,
    "graphical": Graphical,
    "devcontainer": DevContainer,
    "conda_environment": CondaEnvironment,
}


@asi
@dataclass
class Config(_Builder):
    images = {
        "root": Image(),
        "user": Image(),
    }
    container: Container = Container()
    user_settings: UserSettings = UserSettings()

    @classmethod
    def load_conman_config_file(
        cls, filename: Path = ".conman-config.yml"
    ) -> None:
        dic = utils.load_yml_file(yml_filename=filename)
        return cls.from_dic(dic)

    def dump_conman_config_file(
        self, filename: Path = ".conman-config.yml"
    ) -> None:

        with open(filename, "w") as f:
            f.write(yaml.dump(self.__dict__, default_flow_style=False))


if __name__ == "__main__":
    # config_file = "../templates/empty_template_.conman-config.yml"
    # # config_file = "./test.yml"
    # config = Config().load_conman_config_file(filename=config_file)
    # print(config.container.gpu.count)
    config = Config()
    config.dump_conman_config_file(filename="test.yml")

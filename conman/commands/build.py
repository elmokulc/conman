from __future__ import annotations

from typing import Any, Dict, List, Optional, Union, Protocol
from pathlib import Path

import os
from conman import utils
from conman.io import asi, Builder
import conman.ressources as rsrc
from conman.constants import *
import yaml
from dataclasses import dataclass, field
from conman.ressources.devcontainer import DevContainer


@asi
@dataclass
class CondaEnvironment(Builder):

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
@dataclass
class Image(Builder):
    generate: bool = False
    name: str = "<image_name>"
    tag: str = "<image_tag>"
    from_image: Dict[str, str] = field(
        default_factory=lambda: {"name": "ubuntu", "tag": "20.04"}
    )
    conda_environment: CondaEnvironment = CondaEnvironment()
    extra_instructions: List[str] = field(default_factory=lambda: [])

    def to_dockerfile(self, filename: str = "Dockerfile") -> str:
        ...


@asi
@dataclass
class ImageUser(Builder):
    extra_instructions: List[str] = field(default_factory=lambda: [])
    __private_root_img__: Image = Image()

    def to_dockerfile(self, filename: str = "Dockerfile") -> str:
        ...


@asi
@dataclass
class Graphical(Builder):
    enabled: bool = False
    protocol: str = "x11"

    def x_access() -> None:
        # Give access to X11
        print("Executing xhost +local: ...")
        os.system("xhost +local:")


@asi
@dataclass
class Gpu(Builder):
    enabled: bool = False
    manufacturer: str = "nvidia"
    count: int = 0


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
    __private_class_lib__: Dict = field(
        default_factory=lambda: {
            "build": Build,
            "deploy": Deploy,
        }
    )


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


# @asi
# @dataclass
# class DevContainer(Builder):

#     name: str = "devcontainer_name"
#     extensions: List[str] = field(default_factory=lambda: ["ms-python.python"])
#     dockerComposeFile: str = str(Path("/.docker-compose.yml"))
#     __private_devcontainer__: rsrc.devcontainer.DevContainer() = rsrc.devcontainer.DevContainer()


#     def to_devcontainer_json(self, filename="devcontainer.json") -> None:
#         self.__private_devcontainer__.__dict__.update(self.__dict__)
#         self.__private_devcontainer__.dump_to_json(filename=filename, empty=True, none=False)


@asi
@dataclass
class Container(Builder):
    name: str = "container_name"
    devcontainer: DevContainer = DevContainer()
    main_service: Dict[str, str] = field(
        default_factory=lambda: {"name": "main", "container_name": "whatever"}
    )
    graphical: Graphical = Graphical()
    gpu: Gpu = Gpu()
    __private_compose__ = Compose()

    __private_class_lib__: Dict = field(
        default_factory=lambda: {
            "gpu": Gpu,
            "graphical": Graphical,
            "devcontainer": DevContainer,
            "conda_environment": CondaEnvironment,
        }
    )


@asi
@dataclass
class UserSettings(Builder):
    volumes: List[str] = field(default_factory=lambda: ["../:/workspace"])

    def update_volumes(self, volumes: List[str]) -> None:
        ...

    def check_volumes(self, volumes: List[str]) -> None:
        ...


@asi
@dataclass
class Images(Builder):
    root: Image = Image()
    user: ImageUser = ImageUser(__private_root_img__=Image())
    __private_class_lib__: Dict = field(
        default_factory=lambda: {
            "root": Image,
            "user": ImageUser,
        }
    )


@asi
@dataclass
class Config(Builder):
    images: Images = Images()
    container: Container = Container()
    user_settings: UserSettings = UserSettings()
    __private_class_lib__: Dict = field(
        default_factory=lambda: {
            "images": Images,
            "root": Image,
            "user": ImageUser,
            "user_settings": UserSettings,
            "container": Container,
            "gpu": Gpu,
            "graphical": Graphical,
            "devcontainer": DevContainer,
            "conda_environment": CondaEnvironment,
        }
    )

    def __post_init__(self):
        self._check_images()

    def _check_images(self):
        # Update user image definition
        self.images.user.__private_root_img__ = self.images.root

    @classmethod
    def load_conman_config_file(
        cls, filename: Path = ".conman-config.yml"
    ) -> None:
        dic = utils.load_yml_file(yml_filename=filename)
        cls.__private_class_lib__ = {
            "images": Images,
            "root": Image,
            "user": ImageUser,
            "user_settings": UserSettings,
            "container": Container,
            "gpu": Gpu,
            "graphical": Graphical,
            "devcontainer": DevContainer,
            "conda_environment": CondaEnvironment,
        }

        # # Use ipython debugger
        # import ipdb; ipdb.set_trace()

        return cls.from_dic(dic)

    def dump_conman_config_file(
        self, filename: Path = ".conman-config.yml"
    ) -> None:
        # Prettify the config file
        config_msg = (
            "# Conman Configuration File\n"
            + "# Please take your time and carefully complete this file.\n"
            + "# < Authored by: C. Elmo and L. Charleux >\n"
        )
        self.dump_to_yml(filename=filename, preambule=config_msg)

    def run_building(self) -> None:
        self.wdir = os.getcwd() + "/"
        self.build_devcontainer()
        self.build_dockercompose_file()
        self.build_dockerfile_user()
        self.build_dockerfile_root()

    def build_devcontainer(self) -> None:
        if hasattr(config.container, "devcontainer"):
            self.wdir += ".devcontainer/"
            # make directory .devcontainer if not exists
            if not os.path.isdir(".devcontainer"):
                os.mkdir(".devcontainer")
                print("Directory .devcontainer created")

            self.build_devcontainer_json()

    def build_devcontainer_json(self) -> None:
        # create devcontainer.json file
        if not os.path.isfile(".devcontainer/devcontainer.json"):
            print("Creating devcontainer.json file...")
            self.container.devcontainer.to_devcontainer_json()
            print("devcontainer.json file created")
        else:
            print("devcontainer.json file already exists")

    def build_dockercompose_file(self) -> None:
        # create docker-compose.yml file
        if not os.path.isfile("docker-compose.yml"):
            print("Creating docker-compose.yml file...")
            self.container.__private_compose__.to_docker_compose(
                filename=f"{self.wdir}docker-compose.yml"
            )
            print(f"{self.wdir}docker-compose.yml file created")
        else:
            print(f"{self.wdir}docker-compose.yml file already exists")

    def build_dockerfile_user(self) -> None:
        # create Dockerfile.user file
        if not os.path.isfile("Dockerfile.user"):
            print("Creating Dockerfile.user file...")
            self.images.user.to_dockerfile(
                filename=f"{self.wdir}Dockerfile.user"
            )
            print(f"{self.wdir}Dockerfile.user file created")
        else:
            print(f"{self.wdir}Dockerfile.user file already exists")

    def build_dockerfile_root(self) -> None:
        # create Dockerfile.root file
        if self.images.root.generate:
            if not os.path.isfile("Dockerfile.root"):
                print("Creating Dockerfile.root file...")
                self.images.root.to_dockerfile(
                    filename=f"{self.wdir}Dockerfile.root"
                )
                print(f"{self.wdir}Dockerfile.root file created")
            else:
                print(f"{self.wdir}Dockerfile.root file already exists")


def build():
    # TODO
    pass


if __name__ == "__main__":
    config_file = "test_in.yml"
    # config_file = "./test.yml"
    config = Config().load_conman_config_file(filename=config_file)
    # print(config.container.gpu.count)
    # config = Config()
    config.dump_conman_config_file(filename="test_out.yml")
    config.container.devcontainer.dump_devcontainerjson_file()

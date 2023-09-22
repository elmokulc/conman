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
from conman.ressources.docker_compose import DockerComposeFile, DockerCompose
from conman.ressources.docker_file import DockerFile


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
        docker_file = DockerFile()
        docker_file.default_debian_root_instruction(
            base_image=f"{self.from_image.name}:{self.from_image.tag}",
            conda_obj=self.conda_environment,
        )
        for ins in self.extra_instructions:
            docker_file.add_instruction(ins)
        docker_file.generate(filename=filename)


@asi
@dataclass
class ImageUser(Builder):
    extra_instructions: List[str] = field(default_factory=lambda: [])
    __private_root_img__: Image = Image()

    def to_dockerfile(
        self, filename: str = "Dockerfile", graphical=False
    ) -> str:
        docker_file = DockerFile()
        docker_file.default_user_instruction(graphical=graphical)
        for ins in self.extra_instructions:
            docker_file.add_instruction(ins)
        docker_file.generate(filename=filename)


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


@asi
@dataclass
class Container(Builder):
    docker_compose: DockerCompose = DockerCompose()
    devcontainer: DevContainer = DevContainer()
    graphical: Graphical = Graphical()
    gpu: Gpu = Gpu()

    __private_class_lib__: Dict = field(
        default_factory=lambda: {
            "gpu": Gpu,
            "graphical": Graphical,
            "devcontainer": DevContainer,
            "conda_environment": CondaEnvironment,
            "docker_compose": DockerCompose,
        }
    )

    # def __post_init__(self):
    #     self.docker_compose.add_service("main_service", container_name="my_custom_container" )


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
            "docker_compose": DockerCompose,
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
            "docker_compose": DockerCompose,
        }

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
        self.dump_to_yml(filename=filename, private=True, preambule=config_msg)

    def run_building(self) -> None:
        self.wdir = os.getcwd() + "/"
        self.build_devcontainer()
        self.build_dockercompose_file()
        self.build_dockerfile_user()
        self.build_dockerfile_root()

    def build_devcontainer(self) -> None:
        if hasattr(self.container, "devcontainer"):
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
            self.container.devcontainer.dump_devcontainerjson_file(
                filename=f"{self.wdir}devcontainer.json"
            )
            print("devcontainer.json file created")
        else:
            print("devcontainer.json file already exists")

    def build_dockercompose_file(self) -> None:

        docker_compose_file = DockerComposeFile()
        # Add main_container service
        docker_compose_file.add_service(
            service_name=self.container.docker_compose.service_name,
            container_name=self.container.docker_compose.container_name,
        )
        target_service = docker_compose_file.get_service(
            service_name=self.container.docker_compose.service_name
        )

        if self.container.graphical.enabled:
            target_service.activate_display()

        if self.container.gpu.enabled:
            target_service.deploy.activate_gpu()

        # create docker-compose.yml file
        if not os.path.isfile("docker-compose.yml"):
            print("Creating docker-compose.yml file...")

            docker_compose_file.dump_to_yml(
                filename=f"{self.wdir}docker-compose.yml", private=True
            )
            print(f"{self.wdir}docker-compose.yml file created")
        else:
            print(f"{self.wdir}docker-compose.yml file already exists")

    def build_dockerfile_user(self) -> None:
        def _check_graphical():
            if (
                self.container.graphical.enabled
                and self.container.graphical.protocol == "x11"
            ):
                return True
            else:
                return False

        # create Dockerfile.user file
        if not os.path.isfile("Dockerfile.user"):
            print("Creating Dockerfile.user file...")
            self.images.user.to_dockerfile(
                filename=f"{self.wdir}Dockerfile.user",
                graphical=_check_graphical(),
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

    print("Building...")
    config = Config().load_conman_config_file(filename=CONFIG_FILE)
    config.run_building()


if __name__ == "__main__":
    config_file = "test_in.yml"
    # config_file = "./test.yml"
    config = Config().load_conman_config_file(filename=config_file)
    # print(config.container.gpu.count)
    # config = Config()
    # config.dump_conman_config_file(filename="test_out.yml")
    # config.container.devcontainer.dump_devcontainerjson_file()

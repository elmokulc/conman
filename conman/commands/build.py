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
from conman.ressources.docker_file import DockerFile, Instructions
import logging


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
    name: str = "<root_image_name>"
    tag: str = "<root_image_tag>"
    from_image: Dict[str, str] = field(
        default_factory=lambda: {"name": "ubuntu", "tag": "20.04"}
    )
    conda_environment: CondaEnvironment = CondaEnvironment()
    extra_instructions: List[str] = field(default_factory=lambda: [])

    # _optional_attributes_: List[str] = field(
    #     default_factory=lambda: [
    #         "from_image",
    #         "extra_instructions"
    #     ]
    # )

    def to_dockerfile(self, filename: str = "Dockerfile") -> str:
        print("--- Build root Dockerfile ---")
        docker_file = DockerFile(
            img_basename=f"{self.from_image.name}:{self.from_image.tag}",
            conda_environment=self.conda_environment,
        )
        docker_file.default_debian_root_instruction()
        if self.extra_instructions:
            print("Adding root extra instructions to Dockerfile...")
            root_instruction = Instructions.from_lines(
                self.extra_instructions, comment="EXTRA ROOT INSTRUCTIONS"
            )
            docker_file.add_instruction(root_instruction)

        path = os.path.dirname(filename)
        docker_file.generate(filename=filename).dump_build_script(
            filename=path + "/build_root_img.sh",
            enable_nvidia_gpu=self.__parent__.__parent__.check_graphical(),
        )


@asi
@dataclass
class ImageUser(Builder):
    extra_instructions: List[str] = field(default_factory=lambda: [])
    __private_root_img__: Image = Image()

    def to_dockerfile(
        self, filename: str = "Dockerfile", graphical=False
    ) -> str:
        print("--- Build user Dockerfile ---")
        docker_file = DockerFile(
            img_basename=f"{self.__private_root_img__.name}:{self.__private_root_img__.tag}",
            conda_environment=self.__private_root_img__.conda_environment,
        )
        docker_file.default_user_instruction(graphical=graphical)

        if self.__private_root_img__.conda_environment is not None:
            print("Adding conda environment to Dockerfile...")
        else:
            print("No conda environment in root image")

        if self.extra_instructions:
            print("Adding user extra instructions to Dockerfile...")
            user_instruction = Instructions.from_lines(
                self.extra_instructions, comment="EXTRA USER INSTRUCTIONS"
            )
            docker_file.add_instruction(user_instruction)
        else:
            print("No extra instructions in user image")
            user_instruction = Instructions.from_lines(
                ["RUN echo 'No user extra instructions'"],
                comment="EXTRA USER INSTRUCTIONS",
            )
            docker_file.add_instruction(user_instruction)

        docker_file.default_user_end_instruction()

        docker_file.generate(filename=filename)


@asi
@dataclass
class Graphical(Builder):
    # enabled: bool = False
    protocol: str = "x11"

    def x_access() -> None:
        # Give access to X11
        print("Executing xhost +local: ...")
        os.system("xhost +local:")


@asi
@dataclass
class Gpu(Builder):
    # enabled: bool = False
    manufacturer: str = "nvidia"
    count: int = 0


@asi
@dataclass
class Container(Builder):
    docker_compose: DockerCompose = DockerCompose()
    devcontainer: Optional[DevContainer] = DevContainer()
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

    def __post_init__(self):
        self.docker_compose.__parent__ = self
        self.devcontainer.__parent__ = self
        self.graphical.__parent__ = self
        self.gpu.__parent__ = self

        self.devcontainer.service = self.docker_compose.service_name
        self.devcontainer.dockerComposeFile = self.docker_compose.filename


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
    user: ImageUser = ImageUser(__private_root_img__=root)
    __private_class_lib__: Dict = field(
        default_factory=lambda: {
            "root": Image,
            "user": ImageUser,
        }
    )

    def __post_init__(self):
        self.user.__parent__ = self
        self.root.__parent__ = self


@asi
@dataclass
class Config(Builder):
    images: Images = Images()
    container: Container = Container()
    __private_class_lib__: Dict = field(
        default_factory=lambda: {
            "images": Images,
            "root": Image,
            "user": ImageUser,
            "container": Container,
            "gpu": Gpu,
            "graphical": Graphical,
            "devcontainer": DevContainer,
            "conda_environment": CondaEnvironment,
            "docker_compose": DockerCompose,
        }
    )
    _dump_options: Dict = field(
        default_factory=lambda: {
            "rm_private": True,
            "rm_optional": True,
            "rm_empty": False,
            "rm_none": False,
        }
    )

    def __post_init__(self):
        self._check_images()
        self.images.__parent__ = self
        self.container.__parent__ = self

    def _check_images(self):
        # Update user image definition
        self.images.user.__private_root_img__ = self.images.root

    @classmethod
    def load_conman_config_file(
        cls, filename: Path = ".conman-config.yml"
    ) -> None:
        dic = utils.load_yml_file(yml_filename=filename)

        instance = cls.from_dic(dic)
        instance.__private_yml_dic = dic

        for key in dic:
            if hasattr(instance, key):
                attr = getattr(instance, key)
                attr = Config.deletion(obj=attr, dic=dic[key])
                setattr(instance, key, attr)

        return instance

    @staticmethod
    def deletion(obj, dic):
        attrs = []
        for attr in obj.__dict__.keys():
            if attr not in dic and not attr.startswith("__"):
                attrs.append(attr)

        for attr in attrs:
            print(f"Deleting {attr} from {obj.__class__.__name__}")
            setattr(obj, attr, None)

        return obj

    def dump_conman_config_file(
        self,
        filename: Path = ".conman-config.yml",
    ) -> None:
        # Prettify the config file
        config_msg = (
            "# Conman Configuration File\n"
            + "# Please take your time and carefully complete this file.\n"
            + "# < Authored by: C. Elmo and L. Charleux >\n"
        )

        self.dump_to_yml(
            filename=filename, preambule=config_msg, **self._dump_options
        )

    def run_building(self) -> None:
        try:
            self.wdir = os.getcwd() + "/"
            self.build_devcontainer()
            self.build_dockercompose_file()
            self.build_dockerfile_user()
            self.build_dockerfile_root()

            print("Project Building done successfully")
        except Exception as e:
            print("Project Building failed\n", e)
            if DEBUG:
                logging.exception(e)

    def build_devcontainer(self) -> None:
        if self.container.devcontainer is not None:
            self.wdir += ".devcontainer/"
            # make directory .devcontainer if not exists
            if not os.path.isdir(".devcontainer"):
                os.mkdir(".devcontainer")
                print("Directory .devcontainer created")

            print("Creating devcontainer.json file...")
            # create devcontainer.json file
            self.container.devcontainer.dump_devcontainerjson_file(
                filename=f"{self.wdir}devcontainer.json"
            )
        else:
            print("No devcontainer section in config file")

    def build_dockercompose_file(self) -> None:
        # Add main_container service
        self.container.docker_compose._docker_compose_file.add_service(
            service_name=self.container.docker_compose.service_name,
            container_name=self.container.docker_compose.container_name,
        )
        target_service = (
            self.container.docker_compose._docker_compose_file.get_service(
                service_name=self.container.docker_compose.service_name
            )
        )

        # Options management (adding args  eventually to the service)
        # Graphical forwarding
        if self.container.graphical is not None:
            target_service.activate_display()
        # Volume mounting
        target_service.appending_volumes(self.container.docker_compose.volumes)

        # Gpu enabling
        if self.container.gpu is not None:
            target_service.deploy.activate_gpu()

        # Conda enabling
        if self.images.root.conda_environment is not None:
            target_service.activate_conda(
                conda_env_name=self.images.root.conda_environment.env_name
            )

        # create docker-compose.yml file
        self.container.docker_compose._docker_compose_file.dump_to_yml(
            filename=f"{self.wdir}{self.container.docker_compose.filename}",
            rm_private=True,
        )

    def build_dockerfile_user(self) -> None:

        # create Dockerfile.user file
        self.images.user.to_dockerfile(
            filename=f"{self.wdir}Dockerfile.user",
            graphical=self.check_graphical(),
        )

    def build_dockerfile_root(self) -> None:
        # create Dockerfile.root file
        if self.images.root.generate:
            self.images.root.to_dockerfile(
                filename=f"{self.wdir}Dockerfile.root"
            )

    def check_graphical(self) -> bool:
        if self.container.graphical is not None:
            if self.container.graphical.protocol == "x11":
                return True
        else:
            return False


def build():
    print("Building...")

    config = Config().load_conman_config_file(filename=CONFIG_FILE)

    config.run_building()


if __name__ == "__main__":
    build()

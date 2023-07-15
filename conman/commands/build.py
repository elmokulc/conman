from __future__ import annotations

from typing import Any, Dict, List, Optional, Union, Protocol
from pathlib import Path

import os
from conman import utils
from conman.constants import *
import yaml
from dataclasses import dataclass, field
import copy


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
@dataclass
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
@dataclass
class Image(_Builder):
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
class ImageUser(_Builder):
    extra_instructions: List[str] = field(default_factory=lambda: [])
    __private_root_img__: Image = Image()

    def to_dockerfile(self, filename: str = "Dockerfile") -> str:
        ...


@asi
@dataclass
class Graphical(_Builder):
    enabled: bool = False
    protocol: str = "x11"

    def x_access() -> None:
        # Give access to X11
        print("Executing xhost +local: ...")
        os.system("xhost +local:")


@asi
@dataclass
class Gpu(_Builder):
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
@dataclass
class DevContainer(_Builder):
    enabled: bool = True
    name: str = "devcontainer_name"
    extensions: List[str] = field(default_factory=lambda: ["ms-python.python"])

    def to_devcontainer_json(self, filename="devcontainer.json") -> None:
        # TODO

        pass


@asi
@dataclass
class Container(_Builder):
    name: str = "container_name"
    devcontainer: DevContainer = DevContainer()
    main_service: Dict[str, str] = field(
        default_factory=lambda: {"name": "main", "container_name": "whatever"}
    )
    graphical: Graphical = Graphical()
    gpu: Gpu = Gpu()
    __private_compose__ = Compose()


@asi
@dataclass
class UserSettings(_Builder):
    volumes: List[str] = field(default_factory=lambda: ["../:/workspace"])

    def update_volumes(self, volumes: List[str]) -> None:
        ...

    def check_volumes(self, volumes: List[str]) -> None:
        ...


@asi
@dataclass
class Images(_Builder):
    root: Image = Image()
    user: ImageUser = ImageUser(__private_root_img__=Image())


CONFIG = {
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


@asi
@dataclass
class Config(_Builder):
    images: Images = Images()
    container: Container = Container()
    user_settings: UserSettings = UserSettings()

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
        return cls.from_dic(dic)

    def dump_conman_config_file(
        self, filename: Path = ".conman-config.yml"
    ) -> None:

        data = Config.remove_private_attributes(self.copy())
        stream = yaml.dump(
            data,
            default_flow_style=False,
            sort_keys=False,
            indent=4,
        )

        # Prettify the config file
        config_msg = (
            "# Conman Configuration File\n"
            + "# Please take your time and carefully complete this file.\n"
            + "# < Authored by: C. Elmo and L. Charleux >\n"
        )

        stream = config_msg + stream
        prim_attrs = [key for key in config.__dataclass_fields__]
        for attr in prim_attrs:
            stream = stream.replace(
                f"\n{attr}:\n",
                f"\n\n# {attr.capitalize()} Settings\n{attr}:\n",
            )

        # Actually write the file
        with open(filename, "w") as f:
            f.write(stream)

    def copy(self) -> Config:
        return copy.deepcopy(self)

    @staticmethod
    def remove_private_attributes(obj) -> None:
        attributes = obj.__dict__
        private_attributes = []
        for attr, value in attributes.items():
            if attr.startswith("__private_"):
                private_attributes.append(attr)
            elif hasattr(value, "__dict__"):
                Config.remove_private_attributes(value)

        for attr in private_attributes:
            delattr(obj, attr)

        return obj

    @staticmethod
    def remove_empty_attributes(obj):
        # Get all attributes of the object
        attributes = obj.__dict__

        # Iterate through attributes and remove empty ones
        empty_attributes = []
        for attr, value in attributes.items():
            if isinstance(value, (list, dict)):
                # Case where the attribute is a list or a dictionary
                if not value:
                    empty_attributes.append(attr)
            elif hasattr(value, "__dict__"):
                # Case where the attribute is an instance of a class
                Config.remove_empty_attributes(value)
                if not value.__dict__:
                    empty_attributes.append(attr)
            elif not value:
                # General case where the attribute is empty
                empty_attributes.append(attr)

        # Remove empty attributes from the object
        for attr in empty_attributes:
            delattr(obj, attr)

    def run_building(self) -> None:
        self.wdir = os.getcwd() + "/"
        self.build_devcontainer()
        self.build_dockercompose_file()
        self.build_dockerfile_user()
        self.build_dockerfile_root()

    def build_devcontainer(self) -> None:
        if config.container.devcontainer.enabled:
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


if __name__ == "__main__":

    config_file = "../templates/empty_template_.conman-config.yml"
    # config_file = "./test.yml"
    config = Config().load_conman_config_file(filename=config_file)
    # print(config.container.gpu.count)
    # config = Config()
    config.dump_conman_config_file(filename="test.yml")

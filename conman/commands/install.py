from __future__ import annotations

import os
from string import Template
import json
import shutil
import platform
import yaml

from conman import utils
from conman.constants import *
import conman.ressources as rsrc


class Container:
    @classmethod
    def from_dic(cls, dic):
        kwargs = {}
        flag = False
        for key, value in dic.items():
            if key in CONFIG:
                _class = CONFIG[key]
            else:
                flag = True
                _class = Container

            if value.__class__ == dict:
                kwargs[key] = _class.from_dic(value)
            else:
                kwargs[key] = value

        return cls(**kwargs)

    def __init__(self, **kwargs) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)


from conman.config.image import Image

CONFIG = {"image": Image}


class Config(Container):
    def __init__(self, image, volumes, conda, graphical, gpu, container):
        self.image = image
        self.volumes = volumes
        self.conda = conda
        self.graphical = graphical
        self.gpu = gpu
        self.container = container
        self.status_error = 0
        self.build_extra_attr()
        self.check_config_file()

    @classmethod
    def load_from_yml(cls, yml_filename: str) -> Config:
        dic = utils.load_yml_file(yml_filename=yml_filename)
        return cls.from_dic(dic)

    def build_extra_attr(self):
        self.base_name = f"{self.image.name}:{self.image.tag}"

    def check_config_file(self):
        print("Checking config file ...")
        checks = [self.check_image(), self.check_volumes(), self.check_conda()]
        for c in checks:
            self.status_error = c
            if c == 1:
                return c
        return 0

    def check_image(self):
        if self.base_name == "your_image_name:your_image_tag":
            print("Error: base_name is not valid")
            print(f"\t=> Current name is <{self.base_name}>")
            return 1
        else:
            print(f"base_name = {self.base_name}")
            return 0

    def check_volumes(self):
        # Check volumes
        if not self.volumes:
            print("Warning: no volumes specified")
            return 2
        else:
            # Print volumes
            print("volumes:")
            for volume in self.volumes:
                print(f" - {volume}")
            return 0

    def check_conda(self):
        print(f"conda prefix = {self.conda.prefix}")
        print(f"conda env name = {self.conda.env_name}")
        return 0

    def run_config(self):
        return None


def replace_data_in_template(template_filename, data):
    template_path = utils.get_template_file_path(template_filename)
    dct = Template(open(template_path).read().strip()).substitute(data)
    dct = dct.strip()
    return dct


def install_devcontainer(config):
    # make directory .devcontainer if not exists
    if not os.path.isdir(".devcontainer"):
        os.mkdir(".devcontainer")
        print("Directory .devcontainer created")

    data = {
        "CONTAINER_NAME": config.container.devcontainer.name,
        "MAIN_SERVICE_NAME": config.container.main_service.name,
    }

    # read template file empty_template_devcontainer.json from templates directory
    template_filename = "empty_template_devcontainer.json"
    dct = replace_data_in_template(template_filename, data)
    open(".devcontainer/devcontainer.json", "w").write(dct)


def install_dockerfile(config):
    dockerfile = rsrc.docker.DockerFile()
    dockerfile.add("ARG", "BASE_IMAGE", comments="ARG BASE_IMAGE")
    dockerfile.add("FROM", "${BASE_IMAGE}", comments="FROM ${BASE_IMAGE}")
    if config.graphical.enabled and config.graphical.protocol == "x11":
        dockerfile.add(
            "ARG",
            ["USER_NAME", "USER_UID", "USER_GID", "CONDA_ENV_NAME", "DISPLAY"],
            comments="ARGS",
        )
        dockerfile.add(
            "ENV",
            [
                "USER_NAME=${USER_NAME}",
                "USER_GID=${USER_GID}",
                "USER_UID=${USER_UID}",
                "CONDA_ENV_NAME=${CONDA_ENV_NAME}",
                "CONDA_ENV_PATH=/opt/conda/envs/${CONDA_ENV_NAME}/bin/",
                "DISPLAY=${DISPLAY}",
            ],
        )

        dockerfile.add(
            "RUN",
            "apt-get update \\ \n && apt-get install -y sudo x11-apps xauth",
        )

    else:
        dockerfile.add(
            "ARG",
            ["USER_NAME", "USER_UID", "USER_GID", "CONDA_ENV_NAME"],
            comments="ARGS",
        )
        dockerfile.add(
            "ENV",
            [
                "USER_NAME=${USER_NAME}",
                "USER_GID=${USER_GID}",
                "USER_UID=${USER_UID}",
                "CONDA_ENV_NAME=${CONDA_ENV_NAME}",
                "CONDA_ENV_PATH=/opt/conda/envs/${CONDA_ENV_NAME}/bin/",
            ],
            comments="ENV VARIABLES",
        )

    dockerfile.add(
        "RUN",
        [
            f"mkdir -p /etc/sudoers.d",
            f"groupadd --gid $USER_GID $USER_NAME \\ \n    && useradd --uid $USER_UID --gid $USER_GID -m $USER_NAME",
            f"echo $USER_NAME ALL=\\(root\\) NOPASSWD:ALL > /etc/sudoers.d/$USER_NAME \\ \n   && chmod 0440 /etc/sudoers.d/$USER_NAME",
            "usermod -a -G root ${USER_NAME}",
        ],
        comments="USER CREATION",
    )
    dockerfile.add(
        "USER", f"${{USER_UID}}:${{USER_GID}}", comments="Log as $USER"
    )

    dockerfile.add(
        cmds=["SHELL", "ENTRYPOINT"],
        arguments=['["/bin/bash", "--login", "-c"]', '["/bin/bash"]'],
    )

    # Dump docker-compose.yml
    wdir = os.getcwd() + "/"
    if config.container.devcontainer.enabled:
        install_devcontainer(config)
        wdir += ".devcontainer/"

    dockerfile.generate(wdir + "Dockerfile-conman")


def x_access():
    # Give access to X11
    print("Executing xhost +local: ...")
    os.system("xhost +local:")


def install_docker_compose(config):
    docker_compose = rsrc.docker_compose.DockerCompose(
        compose_img_name=config.container.name
    )
    docker_compose.add_service(
        f"{config.container.main_service.name}",
        container_name=f"{config.container.main_service.container_name}",
    )

    current_service = getattr(
        docker_compose.services, f"{config.container.main_service.name}"
    )

    if config.gpu.enabled and config.gpu.manufacturer == "nvidia":
        current_service.deploy.activate_gpu(
            driver=f"{config.gpu.manufacturer}", count=f"{config.gpu.count}"
        )
    else:
        del current_service.deploy

    if config.graphical.enabled and config.graphical.protocol == "x11":
        current_service.activate_display()
        x_access()

    # Add Base image
    current_service.build.add_arg(
        arg_name="BASE_IMAGE", arg_value=config.base_name
    )

    # Add conda configuration
    current_service.build.add_arg(
        arg_name="CONDA_ENV_NAME", arg_value=config.conda.env_name
    )
    current_service.build.add_arg(
        arg_name="CONDA_PREFIX", arg_value=config.conda.prefix
    )

    # Appends volumes
    current_service.volumes += config.volumes

    # Dump docker-compose.yml
    wdir = os.getcwd() + "/"
    if config.container.devcontainer.enabled:
        install_devcontainer(config)
        wdir += ".devcontainer/"

    docker_compose.export(file_path=wdir + "docker-compose.yml")

    return 0


def install(debug=False):
    config_filename = CONFIG_FILE
    if debug:
        config_filename = utils.get_tests_dir() + config_filename

    config = Config.load_from_yml(yml_filename=config_filename)

    install_docker_compose(config)
    install_dockerfile(config)

    return config


if __name__ == "__main__":
    temp = install(debug=True)

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

CONFIG = {
    "root_image": Image,
    "from_image": Image,
    "user_image": Image,
}


class Config(Container):
    def __init__(
        self, root_image, user_image, volumes, graphical, gpu, container
    ):
        self.root_image = root_image
        self.user_image = user_image
        self.volumes = volumes
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
        pass

    def check_config_file(self):
        print("Checking config file ...")
        checks = [self.check_image(), self.check_volumes(), self.check_conda()]
        for c in checks:
            self.status_error = c
            if c == 1:
                return c
        return 0

    def check_image(self):
        if self.user_image.basename == "your_image_name:your_image_tag":
            print("Error: basename is not valid")
            print(f"\t=> Current name is <{self.user_image.basename}>")
            return 1
        else:
            print(f"basename = {self.user_image.basename}")
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
        print(f"conda direcotry = {self.root_image.conda.directory}")
        print(f"conda env name = {self.root_image.conda.env_name}")
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


def x_access():
    # Give access to X11
    print("Executing xhost +local: ...")
    os.system("xhost +local:")


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
        arg_name="BASE_IMAGE", arg_value=config.root_image.basename
    )

    # Add conda configuration
    current_service.build.add_arg(
        arg_name="CONDA_ENV_NAME", arg_value=config.root_image.conda.env_name
    )
    current_service.build.add_arg(
        arg_name="CONDA_DIRECTORY", arg_value=config.root_image.conda.directory
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


def install_dockerfile_user(config):
    dockerfile = rsrc.docker_file.DockerFile()
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
        "RUN",
        ["conda init", 'echo "conda activate $CONDA_ENV_NAME" >> ~/.bashrc'],
        comments="Intialize conda and activate conda environment",
    )

    # Adding extra instructions if any
    if config.user_image.extra_instructions:
        print("Extra instructions found. Adding them to Dockerfile")
        for ind, instruction in enumerate(
            config.user_image.extra_instructions
        ):
            print(f"Adding: \t{instruction}")
            if ind == 0:
                dockerfile.add_line(
                    instruction, comments="----Extra instructions----"
                )
            else:
                dockerfile.add_line(instruction)

    # Dump Dockerfile
    wdir = os.getcwd() + "/"
    if config.container.devcontainer.enabled:
        install_devcontainer(config)
        wdir += ".devcontainer/"

    dockerfile.closing_file().generate(wdir + "Dockerfile-user")


def install_dockerfile_root(config):
    wdir = os.getcwd() + "/"
    # Create a Dockerfile object
    dockerfile = rsrc.docker_file.DockerFile()

    debian_os = ["debian", "ubuntu"]
    if config.root_image.from_image.name not in debian_os:
        raise Exception(
            f"Image {config.root_image.from_image.name} not supported yet.\nSupported images are: {debian_os}"
        )

    dockerfile.add(
        "FROM",
        f"{config.root_image.from_image.basename}",
        comments="Source image",
    )

    # Set Debian frontend to noninteractive
    dockerfile.add("ENV", 'DEBIAN_FRONTEND="noninteractive" TZ="Europe/Paris"')

    # Add basics libraries
    dockerfile.add("RUN", "apt-get update", comments="Updating apt cache")

    dockerfile.add(
        "RUN",
        "apt-get install -y build-essential cmake libncurses5-dev libncursesw5-dev libv4l-dev libxcursor-dev libxcomposite-dev libxdamage-dev libxrandr-dev libxtst-dev libxss-dev libdbus-1-dev libevent-dev libfontconfig1-dev libcap-dev libpulse-dev libudev-dev libpci-dev libnss3-dev libasound2-dev libegl1-mesa-dev",
        comments="Development Tools and Libraries",
    )

    dockerfile.add(
        "RUN", "apt-get install -y ffmpeg", comments="Multimedia libraries"
    )

    dockerfile.add(
        "RUN",
        "apt-get update && apt-get install -y x11-apps xauth",
        comments="X11 libraries",
    )

    dockerfile.add(
        "RUN",
        "apt-get install -y git wget sudo gperf bison nodejs htop",
        comments="Other libraries",
    )

    dockerfile.add(
        "RUN",
        [
            "apt install locales",
            "locale-gen en_US.UTF-8",
            "dpkg-reconfigure locales",
        ],
        comments="Locales update",
    )

    dockerfile.add("RUN", "apt-get clean", comments="Cleaning apt cache")

    # Conda settings and installation
    if config.root_image.conda.enabled:
        conda_directory = config.root_image.conda.directory
        conda_env_name = config.root_image.conda.env_name
        environment_file = config.root_image.conda.environment_file
        # Add conda arguments
        dockerfile.add(
            "ARG",
            [
                f"CONDA_DIRECTORY={conda_directory}",
                f"CONDA_ENV_NAME={conda_env_name}",
            ],
            comments="CONDA ARGS",
        )

        # Define conda environment variables
        dockerfile.add(
            "ENV",
            [
                "CONDA_DIRECTORY $CONDA_DIRECTORY",
                "CONDA_ENV_NAME $CONDA_ENV_NAME",
                "CONDA_BIN_PATH $CONDA_DIRECTORY/condabin/conda",
                "CONDA_ENV_BIN_PATH $CONDA_DIRECTORY/envs/$CONDA_ENV_NAME/bin",
                "CONDA_ENV_PATH $CONDA_DIRECTORY/envs/$CONDA_ENV_NAME",
            ],
            comments="Conda environment variables",
        )

        # Add conda executable to PATH

        dockerfile.add(
            "ENV",
            "PATH $CONDA_DIRECTORY/condabin/:$PATH",
            comments="Add conda executable to PATH",
        )

        # Setting umask to 0000

        dockerfile.add(
            "RUN",
            [
                'line_num=$(cat /etc/pam.d/common-session | grep -n umask | cut -d: -f1 | tail -1) && \ \n\tsed -i "${line_num}s/.*/session optional pam_umask.so umask=000/" /etc/pam.d/common-session',
                'line_num=$(cat /etc/login.defs | grep -n UMASK | cut -d: -f1 | tail -1) && \ \n\tsed -i "${line_num}s/.*/UMASK               000/" /etc/pam.d/common-session',
                "echo 'umask 000' >> ~/.profile",
            ],
            comments="Setting umask",
        )

        # Installing miniconda
        dockerfile.add(
            "RUN",
            "umask 000 && \ \n\tmkdir -p ${CONDA_DIRECTORY} && \ \n\tchmod 777 ${CONDA_DIRECTORY} && \ \n\twget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \ \n\tbin/bash ~/miniconda.sh -ub -p $CONDA_DIRECTORY && \ \n\trm ~/miniconda.sh",
            comments="Installing miniconda",
        )

        manage_conda_env_file(environment_file, conda_env_name)

        dockerfile.add(
            ["COPY", "RUN"],
            [
                f"{environment_file} /tmp/environment.yml",
                "umask 000 && \ \n\tconda update -n base conda && \ \n\tconda create -y -n $CONDA_ENV_NAME && \ \n\tconda env update --name $CONDA_ENV_NAME --file /tmp/environment.yml --prune ",
            ],
            comments="Conda env creation",
        )

        dockerfile.add(
            "RUN",
            [
                'echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc',
                'echo "conda activate $CONDA_ENV_NAME" >> ~/.bashrc',
            ],
            comments="Conda env activation for root user",
        )

    # Adding extra instructions if any
    if config.root_image.extra_instructions:
        print("Extra instructions found. Adding them to Dockerfile")
        for ind, instruction in enumerate(
            config.root_image.extra_instructions
        ):
            print(f"Adding: \t{instruction}")
            if ind == 0:
                dockerfile.add_line(
                    instruction, comments="----Extra instructions----"
                )
            else:
                dockerfile.add_line(instruction)

    # Dump Dockerfile
    dockerfile.closing_file().generate(wdir + "Dockerfile")


def build(debug=False):
    config_filename = CONFIG_FILE
    if debug:
        config_filename = utils.get_tests_dir() + config_filename

    config = Config.load_from_yml(yml_filename=config_filename)

    install_docker_compose(config)
    install_dockerfile_user(config)

    if config.root_image.generate:
        install_dockerfile_root(config)

    return config


if __name__ == "__main__":
    temp = install(debug=True)

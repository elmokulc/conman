import yaml
import platform
import os
from conman.io import asi, Builder
from conman.utils import get_random_hash_str
from dataclasses import dataclass, field
from typing import List, Dict, Any


def get_user_id_data():
    """
    Retrieves user ID-related data based on the operating system platform.

    Returns:
        dict: A dictionary containing user ID-related data, including USER_NAME, UID, and GID.
    """

    # Check if the OS platform is Linux or Windows
    if platform.system() == "Linux":
        import pwd

        return {
            "USER_NAME": os.environ.get("USER"),
            "USER_UID": str(pwd.getpwnam(os.environ.get("USER")).pw_uid),
            "USER_GID": str(pwd.getpwnam(os.environ.get("USER")).pw_gid),
        }
    elif platform.system() == "Windows":
        return {
            "USER_NAME": os.environ.get("USER"),
            "USER_UID": "1000",
            "USER_GID": "1000",
        }


def get_display():
    """
    Retrieves the display configuration based on the operating system platform.

    Returns:
        str: The display configuration.
    """

    if platform.system() == "Linux":
        return str(os.environ.get("DISPLAY"))
    else:
        return "host.docker.internal:0"


def x_access():
    # Give access to X11
    print("Executing xhost +local: ...")
    os.system("xhost +local:")


@asi
@dataclass
class DockerComposeFile(Builder):
    version: str = "3.9"
    services: Builder = Builder()

    def add_service(self, service_name, **kwargs):
        """
        Adds a new service to the DockerComposeFile object.

        Args:
            service_name (str): The name of the service.
            **kwargs: Additional keyword arguments to configure the service.

        Returns:
            None
        """

        service = Service(**kwargs)
        self.services.add_field(service_name, service)

    def get_service(self, service_name: str):
        """
        Retrieves the services associated with the DockerComposeFile object.

        Returns:
            list: The list of services.
        """

        return getattr(self.services, service_name)


@asi
@dataclass
class DockerCompose(Builder):
    filename: str = "docker-compose.yml"
    service_name: str = "main_service_name"
    volumes: List[str] = field(default_factory=lambda: ["../:/workspace"])
    _container_name: str = (
        f'{get_user_id_data()["USER_NAME"]}-container-{get_random_hash_str()}'
    )
    _docker_compose_file: DockerComposeFile = DockerComposeFile()


@asi
@dataclass
class Build(Builder):
    """
    A class representing the build configuration for a service in a Docker Compose configuration.

    Inherits from:
        Field: A class representing a field.

    Attributes:
        dockerfile (str): The path to the Dockerfile.
        args (list): Additional arguments for the build process.
        context (str): The build context.

    Methods:
        __init__(self, dockerfile="./Dockerfile", args=[], context=".", **kwargs)
            Initializes a new instance of the Build class.

        get_user_specific_args(self)
            Retrieves user-specific arguments and appends them to the args list.

        get_display(self)
            Retrieves the display configuration and appends it to the args list.

        add_arg(self, arg_name, arg_value)
            Adds a new argument to the args list.

        activate_display(self)
            Activates the display configuration.
    """

    dockerfile: str = "./Dockerfile.user"
    context: str = "."
    args: List[str] = field(default_factory=lambda: [])

    def __post_init__(self):
        self.get_user_specific_args()

    def get_user_specific_args(self):
        """
        Retrieves user-specific arguments and appends them to the args list.

        Returns:
            list: The updated args list.
        """

        user_id_data = get_user_id_data()
        for key, value in user_id_data.items():
            self.args.append(f"{key}={value}")
        return self.args.sort()

    def get_display(self):
        """
        Retrieves the display configuration and appends it to the args list.

        Returns:
            list: The updated args list.
        """

        display = get_display()
        self.args.append(f"DISPLAY={display}")
        return self.args.sort()

    def add_arg(self, arg_name, arg_value):
        """
        Adds a new argument to the args list.

        Args:
            arg_name (str): The name of the argument.
            arg_value (str): The value of the argument.

        Returns:
            None
        """

        self.args.append(f"{arg_name}={arg_value}")
        self.args.sort()


@asi
@dataclass
class Deploy(Builder):
    resources: Builder = Builder()

    def __post_init__(self):
        self.resources.add_field("reservations", Builder())

    def activate_gpu(
        self, driver="nvidia", count: int = 1, capabilities=["gpu"]
    ):
        """
        Activates GPU support for the deployment.

        Args:
            driver (str): The driver to use for GPU support.
            count (int): The number of GPUs to allocate.
            capabilities (list): The capabilities required for the GPUs.

        Returns:
            None
        """

        self.resources.reservations.add_field(
            "devices",
            [
                {
                    "driver": driver,
                    "count": int(count),
                    "capabilities": capabilities,
                }
            ],
        )
        print("-> GPU activated")


@asi
@dataclass
class Service(Builder):
    build: Build = Build()
    deploy: Deploy = Deploy()
    container_name: str = ""
    volumes: List[str] = field(default_factory=lambda: [])
    __private_class_lib__: Dict = field(
        default_factory=lambda: {
            "build": Build,
            "deploy": Deploy,
        }
    )
    """
    A class representing a service in a Docker Compose configuration.

    Inherits from:
        Field: A class representing a field.

    Attributes:
        build (Build): The build configuration for the service.
        deploy (Deploy): The deployment configuration for the service.
        container_name (str): The name of the container.
        volumes (list): The volumes associated with the service.

    Methods:
        __init__(self, container_name="", volumes=[], **kwargs)
            Initializes a new instance of the Service class.

        activate_display(self)
            Activates the display configuration.

        extra_volumes_display(self)
            Adds extra volumes required for display configuration.
    """

    def x_access(self):
        x_access()

    def activate_display(self):
        """
        Activates the display configuration.

        Returns:
            None
        """
        self.x_access()
        self.build.get_display()
        self.extra_volumes_display()
        self.privileged = True
        self.network_mode = "host"
        print("-> Display forwading activated")

    def extra_volumes_display(self):
        """
        Adds extra volumes required for display configuration.

        Returns:
            None
        """

        X_volumes = [
            "/tmp/.X11-unix:/tmp/.X11-unix:rw",
            f"/home/{get_user_id_data()['USER_NAME']}/.Xauthority:/home/{get_user_id_data()['USER_NAME']}/.Xauthority:rw",
        ]
        print("Appending volumes for display configuration...")
        self.appending_volumes(X_volumes)

    def appending_volumes(self, volumes):
        """
        Adds extra volumes required for display configuration.

        Returns:
            None
        """
        [print(f"-> Add volume: {v}") for v in volumes]
        self.volumes += volumes

    def activate_conda(self, conda_env_name):
        """
        Activates the conda configuration.

        Returns:
            None
        """
        self.build.add_arg("CONDA_ENV_NAME", f"{conda_env_name}")


if __name__ == "__main__":
    # Create DockerComposeFile instance
    docker_compose_file = DockerComposeFile()

    # # Add main_container service
    docker_compose_file.add_service(
        "main_service", container_name="my_custom_container"
    )

    # # If you want to add a deploy field for gpu access
    # docker_compose.services.main_service.deploy.activate_gpu()

    # # if you need to enable x forwarding
    # docker_compose.services.main_service.activate_display()

    # Export to docker-compose.yml
    docker_compose_file.dump_to_yml("docker-compose.yml", private=True)

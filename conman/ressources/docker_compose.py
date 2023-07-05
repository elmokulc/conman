import yaml
import platform
import os


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


class Field:
    """
    A class representing a field.

    Attributes:
        N/A

    Methods:
        __init__(self, **kwargs)
            Initializes a new instance of the Field class.

        __repr__(self) -> str
            Returns a string representation of the Field object.

        add_field(self, field, value)
            Adds a new field with the specified value to the Field object.

        field_representer(dumper, data)
            A static method used as a custom YAML representer for Field objects.

        register_repr(self)
            Registers the field_representer as a representer for the Field class in YAML.
    """

    def __init__(self, **kwargs):
        """
        Initializes a new instance of the Field class.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """

        self.register_repr()

    def __repr__(self) -> str:
        """
        Returns a string representation of the Field object.

        Returns:
            str: The string representation of the Field object.
        """

        return self.__dict__.__repr__()

    def add_field(self, field, value):
        """
        Adds a new field with the specified value to the Field object.

        Args:
            field (str): The name of the field to add.
            value (Any): The value of the field.

        Returns:
            None
        """

        self.__dict__[field] = value

    @staticmethod
    def field_representer(dumper, data):
        """
        A static method used as a custom YAML representer for Field objects.

        Args:
            dumper (yaml.Dumper): The YAML dumper object.
            data (Field): The Field object to represent.

        Returns:
            Any: The YAML representation of the Field object.
        """

        return dumper.represent_dict(data.__dict__)

    def register_repr(self):
        """
        Registers the field_representer as a representer for the Field class in YAML.

        Returns:
            None
        """

        yaml.add_representer(self.__class__, Field.field_representer)


@asi
class DockerCompose(Field):
    """
    A class representing a Docker Compose configuration.

    Inherits from:
        Field: A class representing a field.

    Attributes:
        services (Field): The services defined in the Docker Compose configuration.

    Methods:
        __init__(self)
            Initializes a new instance of the DockerCompose class.

        add_service(self, service_name, **kwargs)
            Adds a new service to the DockerCompose object.

        to_yaml(self, version="3.9")
            Converts the DockerCompose object to a YAML string.

        export(self, file_path="docker-compose.yml")
            Exports the DockerCompose object to a YAML file.

    """

    def __init__(self, compose_img_name, version="3.9"):
        """
        Initializes a new instance of the DockerCompose class.
        Args:
            compose_img_name (str): The name of the image created via docker compose.
        Returns:
            None
        """

        self.services = Field()
        self.name = compose_img_name
        self.version = version

    def add_service(self, service_name, **kwargs):
        """
        Adds a new service to the DockerCompose object.

        Args:
            service_name (str): The name of the service.
            **kwargs: Additional keyword arguments to configure the service.

        Returns:
            None
        """

        service = Service(**kwargs)
        self.services.add_field(service_name, service)

    def to_yaml(self):
        """
        Converts the DockerCompose object to a YAML string.

        Returns:
            str: The YAML representation of the DockerCompose object.
        """

        return yaml.dump(self.__dict__, default_flow_style=False)

    def export(self, file_path="docker-compose.yml"):
        """
        Exports the DockerCompose object to a YAML file.

        Args:
            file_path (str): The path to the output YAML file.

        Returns:
            None
        """

        with open(file_path, "w") as f:
            f.write(self.to_yaml())


@asi
class Service(Field):
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

    def __init__(self, container_name="", volumes=[], **kwargs):
        """
        Initializes a new instance of the Service class.

        Args:
            container_name (str): The name of the container.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """

        self.build = Build()
        self.deploy = Deploy()
        self.container_name = container_name
        self.volumes = volumes

    def activate_display(self):
        """
        Activates the display configuration.

        Returns:
            None
        """

        self.build.get_display()
        self.extra_volumes_display()
        self.privileged = True
        self.network_mode = "host"

    def extra_volumes_display(self):
        """
        Adds extra volumes required for display configuration.

        Returns:
            None
        """

        self.volumes += [
            "/tmp/.X11-unix:/tmp/.X11-unix:rw",
            f"/home/{get_user_id_data()['USER_NAME']}/.Xauthority:/home/{get_user_id_data()['USER_NAME']}/.Xauthority:rw",
        ]


@asi
class Build(Field):
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

    def __init__(
        self, dockerfile="./Dockerfile-conman", args=[], context=".", **kwargs
    ):
        """
        Initializes a new instance of the Build class.

        Args:
            dockerfile (str): The path to the Dockerfile.
            args (list): Additional arguments for the build process.
            context (str): The build context.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """

        self.args = args
        self.context = context
        self.dockerfile = dockerfile

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
class Deploy(Field):
    """
    A class representing the deployment configuration for a service in a Docker Compose configuration.

    Inherits from:
        Field: A class representing a field.

    Attributes:
        resources (Field): The resource configuration for the deployment.

    Methods:
        __init__(self, **kwargs)
            Initializes a new instance of the Deploy class.

        activate_gpu(self, driver="nvidia", count=1, capabilities=["gpu"])
            Activates GPU support for the deployment.

    """

    def __init__(self, **kwargs):
        """
        Initializes a new instance of the Deploy class.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """

        self.resources = Field()
        self.resources.add_field("reservations", Field())

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


if __name__ == "__main__":
    # Create DockerCompose instance
    docker_compose = DockerCompose()

    # Add main_container service
    docker_compose.add_service(
        "main_service", container_name="my_custom_container"
    )

    # If you want to add a deploy field for gpu access
    docker_compose.services.main_service.deploy.activate_gpu()

    # if you need to enable x forwarding
    docker_compose.services.main_service.activate_display()

    # Export to docker-compose.yml
    docker_compose.export()

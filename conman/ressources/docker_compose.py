import yaml
import platform 
import os 

def get_user_id_data():
    # check os platform is linux or windows
    if platform.system() == "Linux":
        import pwd
        return {
            "USER_NAME": os.environ.get("USER"),
            "UID": str(pwd.getpwnam(os.environ.get("USER")).pw_uid),
            "GID": str(pwd.getpwnam(os.environ.get("USER")).pw_gid),
        }
        
    elif platform.system() == "Windows":
        return {
            "USER_NAME": os.environ.get("USER"),
            "UID": "1000",
            "GID": "1000",
        }
    
def get_display():   
    if platform.system() == "Linux": 
        return str(os.environ.get("DISPLAY"))
    else: 
        return "host.docker.internal:0"

def asi(subclass):
    """
    asi = activate superclass __init__
    Args:
        subclass (_type_): _description_

    Returns:
        _type_: _description_
    """
    original_init = subclass.__init__

    def new_init(self, *args, **kwargs):
        super(subclass, self).__init__(*args, **kwargs)
        original_init(self, *args, **kwargs)

    subclass.__init__ = new_init
    return subclass

class Field:
    def __init__(self, **kwargs):
        self.register_repr()
        
    def __repr__(self) -> str:
        return self.__dict__.__repr__()
            
    def add_field(self, field, value):
        self.__dict__[field] = value

    @staticmethod
    def field_representer(dumper, data):
        return dumper.represent_dict(data.__dict__)
    
    def register_repr(self):
        yaml.add_representer(self.__class__, Field.field_representer)
    
        
@asi
class DockerCompose(Field):
    def __init__(self):
        self.services = Field()

    def add_service(self, service_name, **kwargs):
        service = Service(**kwargs)
        self.services.add_field(service_name, service)
        
    def to_yaml(self, version="3.9"):
        data = {"version": version}
        data.update(self.__dict__)
        return yaml.dump(data, default_flow_style=False)

    def export(self, file_path="docker-compose.yml"):
        with open(file_path, "w") as f:
            f.write(self.to_yaml())

@asi
class Service(Field): 
    def __init__(self, container_name="", **kwargs):
        self.build = Build()
        self.container_name = container_name

    def activate_gpu_deploy(self):
            self.deploy = Deploy()
@asi
class Build(Field):
    def __init__(self, dockerfile="./Dockerfile", args=[], context=".", **kwargs):
        
        self.args = args
        self.context = context
        self.dockerfile = dockerfile
        
        self.get_user_specific_args()
        self.get_display()

    def get_user_specific_args(self):
        user_id_data = get_user_id_data()
        for key, value in user_id_data.items():
            self.args.append(f"{key}={value}")
        return self.args

    def get_display(self):
        display = get_display()
        self.args.append(f"DISPLAY={display}")
        return self.args
        
    def add_arg(self, arg_name, arg_value):
        self.args.append(f"{arg_name}={arg_value}")
        
        
@asi 
class Deploy(Field):
    
    def __init__(self, resources={}, **kwargs):
        self.resources = resources
        self.set_devices()
    
    def set_devices(self, driver="nvidia", count=0, capabilities=["gpu"]):
        self.resources = {"reservations": {"devices": [{"driver": driver, "count": count, "capabilities": capabilities}]}}
        
        
# Create DockerCompose instance
docker_compose = DockerCompose()

# Add main_container service
docker_compose.add_service("main_service", container_name="my_custom_container")

# If you want to add a deploy field for gpu access
docker_compose.services.main_service.activate_gpu_deploy()

# Export to docker-compose.yml
docker_compose.export()

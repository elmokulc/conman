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

def activate_super_init(subclass):
    original_init = subclass.__init__

    def new_init(self, *args, **kwargs):
        super(subclass, self).__init__(*args, **kwargs)
        original_init(self, *args, **kwargs)

    subclass.__init__ = new_init
    return subclass

class Field:
    def __init__(self):
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
    
        
@activate_super_init
class DockerCompose(Field):
    def __init__(self):
        self.services = Field()

    def add_service(self, service_name):
        service = Service()
        self.services.add_field(service_name, service)
        
    def to_yaml(self, version="3.9"):
        data = {"version": version}
        data.update(self.__dict__)
        return yaml.dump(data, default_flow_style=False)

    def export(self, file_path):
        with open(file_path, "w") as f:
            f.write(self.to_yaml())

@activate_super_init
class Service(Field): pass



# Create DockerCompose instance
docker_compose = DockerCompose()

# Add main_container service
docker_compose.add_service("main_container")
docker_compose.services.main_container.add_field("build", {
    "dockerfile": "./Dockerfile",
    "args": [
        "BASE_IMAGE=$BASE_IMAGE",
        "USER_NAME=$USER_NAME",
        "USER_UID=$UID",
        "USER_GID=$GID",
        "CONDA_ENV_NAME=$CONDA_ENV_NAME",
        "DISPLAY=$DISPLAY"
    ],
    "context": "."
})
docker_compose.services.main_container.add_field("container_name", "$CONTAINER_NAME")
docker_compose.services.main_container.add_field("stdin_open", False)
docker_compose.services.main_container.add_field("deploy", {
    "resources": {
        "reservations": {
            "devices": [
                {
                    "driver": "nvidia",
                    "count": "$GPU_COUNT",
                    "capabilities": ["gpu"]
                }
            ]
        }
    }
})

# Export to docker-compose.yml
docker_compose.export("docker-compose.yml")

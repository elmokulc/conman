import yaml
import platform 
import os 

def add_entry(data: dict, entry: str, value):
        data[entry] = value
        return data[entry]

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

class DockerCompose:
    def __init__(self):
        self.services = {}

    
    def add_service(self, service_name):
        return add_entry(
            data=self.services,
            entry=service_name, 
            value=ServiceData(service_name))
        
    def to_yaml(self, version="3.9"):
        data = {"version": f"{version}", "services": {name: service.to_dict() for name, service in self.services.items()}}
        return yaml.dump(data)

    def export(self, file_path):
        with open(file_path, "w") as f:
            f.write(self.to_yaml())

class ServiceData:
    def __init__(self, service_name):
        self.service_name = service_name
        self.data = {}

    def add_field(self, field, value):
        self.data[field] = value
        
    # def add_args(self, arg, value):
    #     self.data["build"]["args"].append(f"{arg}={value}")
        
    # def set_build(self, context: str = ".",
    #                     dockerfile: str = "./Dockerfile",
    #                     args: list(str) = None,
    #                     image: str = None,
    #                     ):

    #     build = {}
    #     if dockerfile is not None:
    #         build["dockerfile"] = dockerfile
    #     if args is not None:
    #         build["args"] = args

    #     return build
        
    # def add_build(self, build):
    #     self.data["build"] = build

    def to_dict(self):
        return self.data

# Create DockerCompose instance
docker_compose = DockerCompose()

# Add main_container service
main_container_service = docker_compose.add_service("main_container")
main_container_service.add_field("build", {
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
main_container_service.add_field("container_name", "$CONTAINER_NAME")
main_container_service.add_field("stdin_open", False)
main_container_service.add_field("deploy", {
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

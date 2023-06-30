from __future__ import annotations

import os 
from string import Template
import json
import shutil
import platform
import yaml

from conman import utils
from conman.constants import *

class Container:
    @classmethod
    def from_dic(cls, dic):
        kwargs = {}
        flag = False
        for key, value in dic.items():
            if key in CONFIG:
                _class = CONFIG[key]
            else:
                flag =True
                _class = Container
            
            if value.__class__ == dict:
                kwargs[key] = _class.from_dic(value)
            else :
                kwargs[key] = value

                
        return cls(**kwargs)
    
    def __init__(self, **kwargs) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)
            
from conman.config.image import Image
CONFIG = {"image":Image}


class Config(Container):   
            
    def __init__(self, image, volumes, conda, graphical, gpu, container):
        self.image = image
        self.volumes = volumes
        self.conda  = conda
        self.graphical = graphical
        self.gpu = gpu
        self.container = container
        self.status_error = 0
        self.build_extra_attr()
        self.check_config_file()

    @classmethod
    def load_from_yml(cls, yml_filename: str) -> Config:
        dic= utils.load_yml_file(yml_filename=yml_filename)
        return cls.from_dic(dic)
    
    
    def build_extra_attr(self):
        self.base_name = f"{self.image.name}:{self.image.tag}"
    
    def check_config_file(self):
        print("Checking config file ...")
        checks = [self.check_image() , self.check_volumes() , self.check_conda()]
        for c in checks:
            self.status_error = c
            if c == 1: 
                return c
        return 0
        
        
    def check_image(self):
        if self.base_name == 'your_image_name:your_image_tag':
            print("Error: base_name is not valid")
            print(f"\t=> Current name is <{self.base_name}>")
            return 1
        else :
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
        print(f'conda prefix = {self.conda.prefix}')
        print(f'conda env name = {self.conda.env_name}')
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
        
    data = {"CONTAINER_NAME":config.container.devcontainer.name,
            "MAIN_SERVICE_NAME":config.container.main_service_name,
            }
        
    # read template file empty_template_devcontainer.json from templates directory
    template_filename = "empty_template_devcontainer.json"
    dct = replace_data_in_template(template_filename, data)
    open(".devcontainer/devcontainer.json", "w").write(dct)
    
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
       
        

def install_docker_compose(config):
    template_filename = "empty_template_docker-compose.yml"
    wdir = os.getcwd() + "/"
    
    data = {
        "MAIN_SERVICE_NAME":config.container.main_service_name,
        "CONTAINER_NAME":config.container.name,
        "BASE_IMAGE":config.base_name,
        "CONDA_ENV_NAME":config.conda.env_name,
        "DISPLAY":get_display(),
    }
    
    data_user_id = get_user_id_data()
    data.update(data_user_id)
    
    
    if config.container.devcontainer.enabled:
        install_devcontainer(config)
        wdir = os.getcwd() + "/.devcontainer/"
        
    if config.gpu.enabled and config.gpu.manufacturer == "nvidia":
        data.update({"GPU_COUNT":config.gpu.count})
        template_filename = "empty_template_docker-compose-nvidia.yml"
        
    if config.graphical.enabled and config.graphical.protocol == "x11":
        # Need to mount volumes for x11 forwarding
        config.volumes += [
            "/tmp/.X11-unix:/tmp/.X11-unix:rw",
            f"/home/{data_user_id['USER_NAME']}/.Xauthority:root/.Xauthority:rw",
            f"/home/{data_user_id['USER_NAME']}/.Xauthority:/home/{data_user_id['USER_NAME']}/.Xauthority:rw",
        ]
        extra_opt_dict = {"privileged":True, "network_mode":"host"}
        
    dct = replace_data_in_template(template_filename, data)
    
    # Append volumes to docker-compose.yml
    
    data_dict  = yaml.safe_load(dct)
    data_dict["services"][f"{config.container.main_service_name}"]["volumes"] = config.volumes
    if extra_opt_dict:
        data_dict["services"][f"{config.container.main_service_name}"].update(extra_opt_dict)
    
    dct = yaml.dump(data_dict)
    
    open(wdir+"docker-compose.yml", "w").write(dct)
    return data_dict
    
def install(debug=False):  

    config_filename = CONFIG_FILE
    if debug:
         config_filename = utils.get_tests_dir() + config_filename
          
        
    config = Config.load_from_yml(yml_filename=config_filename)
    
    
    return config


if __name__ == "__main__":
    temp = install(debug=True)

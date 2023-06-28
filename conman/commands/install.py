from __future__ import annotations

import os 
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
            
    def __init__(self, image, volumes, conda, graphical, gpu):
        self.image = image
        self.volumes = volumes
        self.conda  = conda
        self.graphical = graphical
        self.gpu = gpu
        self.build_extra_attr()
        self.check_config_file()

    @classmethod
    def load_from_yml(cls, yml_filename: str) -> Config:
        dic= utils.load_yml_file(yml_filename=yml_filename)
        return cls.from_dic(dic)
    
    
    def build_extra_attr(self):
        self.__error_status__ = False
        self.base_name = f"{self.image.name}:{self.image.tag}"
    
    def check_config_file(self):
        print("Checking config file ...")
        def _check_image():
            if self.base_name == 'your_image_name:your_image_tag':
                print("Error: base_name is not valid")
                print(f"\t=> Current name is <{self.base_name}>")
                self.__error_status__ = True
            else :
                print(f"base_name = {self.base_name}")
            
        def _check_volumes():
            # Check volumes
            if not self.volumes: 
                print("Warning: no volumes specified")
            else:
                # Print volumes
                print("volumes:")
                for volume in self.volumes:
                    print(f" - {volume}")
    
        def _check_conda():
            print(f'conda prefix = {self.conda.prefix}')
            print(f'conda env name = {self.conda.env_name}')
    
        # Check if base_name is valid
        _check_image()
        # Check volumes
        _check_volumes()
        # Check conda
        _check_conda()
        
    def run_config(self):
        return None 


def install(debug=False):  

    config_filename = CONFIG_FILE
    if debug:
         config_filename = utils.get_tests_dir() + config_filename
          
        
    config = Config.load_from_yml(yml_filename=config_filename)
    
    
    return config


if __name__ == "__main__":
    temp = install(debug=True)

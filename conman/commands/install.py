from __future__ import annotations

import os 
from conman import utils
from conman.utils import Construct
from conman.constants import *
from conman.config.image import Image


class Config(Construct):   
            
    def __init__(self, **kwargs):
        super().__init__(**kwargs)  
        self.build_extra_attr()
        self.check_config_file()
    
    
    def build_extra_attr(self):
        self.__error_status__ = False
        self.base_name = f"{self.image.name}:{self.image.tag}"
    
    def check_config_file(self):
        
        def _check_image():
            if self.base_name == 'your_image_name:your_image_tag':
                print("Error: base_name is not valid")
                self.__error_status__ = True
            
        def _check_volumes():
            # Check volumes
            if not self.volumes.python_packages: 
                print("Warning: no python_packages added to volumes")
            else:
                # Print the list of python_packages 
                print("python_packages:")
                for package in self.volumes.python_packages:
                    print(f" - {package}")

            if not self.volumes.data:
                print("Warning: no data added to volumes")
            else:
                # Print the list of data
                print("data:")
                for data in self.volumes.data:
                    print(f" - {data}")
                    
            if not self.volumes.hardware:
                print("Warning: no hardware added to volumes")
            else:
                # Print the list of hardware
                print("hardware:")
                for hardware in self.volumes.hardware:
                    print(f" - {hardware}")
    
        def _check_conda():
            print(f'conda prefix = {self.conda.prefix}')
            print(f'conda env name = {self.conda.env_name}')
    
        # Check if base_name is valid
        _check_image()
        # Check volumes
        _check_volumes()
        # Check conda
        _check_conda()
        
            


def install(debug=False):
    print("install() function executed !")
    

    config_filename = CONFIG_FILE
    if debug:
        config_filename = utils.get_template_file_path(config_filename)
          
        
    config = Config(**utils.load_yml_file(yml_filename=config_filename))
    
    
    return config


if __name__ == "__main__":
    temp = install(debug=True)
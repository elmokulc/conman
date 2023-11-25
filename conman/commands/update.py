import os 
import logging
from conman.constants import CONFIG_FILE
from conman.commands.build import Config as Config_build


class Config(Config_build):
    """Update the conman build"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def update_build(self):
        """Update the conman build"""
        try:
            print("Updating conman build...")
            self.wdir = os.getcwd() + "/"
            self.build_devcontainer()
            self.build_dockercompose_file()
            self.build_dockerfile_user()
        except Exception as e:
            print("Project update failed")
            logging.exception(e)
            
        
        


def update():
    """Update the conman build"""
    
    config = Config().load_conman_config_file(filename=CONFIG_FILE)
    config.update_build()
from __future__ import annotations

import os.path
import pkg_resources
import conman
import shutil
import os
import yaml

TEMPLATE_PREFIX = "empty_template_"

def check_is_templatefile(filename: str) -> str:
    if filename.startswith(TEMPLATE_PREFIX):
        return filename
    else:
        return TEMPLATE_PREFIX + filename

def get_template_file_path(template_filename: str) -> str:
    
    module_path = os.path.dirname(__file__)
    template_path = os.path.join(module_path, "templates", check_is_templatefile(template_filename))
    
    return template_path
    

def cp_template_file(template_filename: str) -> None:
    
    wdir = os.getcwd() + "/"
    template_path = get_template_file_path(template_filename)
    shutil.copy(template_path, wdir+template_filename.replace(f"{TEMPLATE_PREFIX}", ""))
    
    return 0
    
def load_yml_file(yml_filename: str) -> dict:
    with open(yml_filename, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    
    # config = convert_to_object(config)
    return config

def convert_to_object(data):
    if isinstance(data, dict):
        obj = type('', (), {})()  # Crée un obj vide
        for key, value in data.items():
            setattr(obj, key, convert_to_object(value))  # Appelle récursivement la fonction pour les sous-dictionnaires
        return obj
    elif isinstance(data, list):
        return [convert_to_object(element) for element in data]
    else:
        return data
    
class Construct:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            try: 
                arg_class = globals()[key.capitalize()]
            except:
                arg_class = Construct
            if value.__class__ == dict:
                setattr(self, key, arg_class(**value))
            else:
                setattr(self, key, value)
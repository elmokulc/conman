from __future__ import annotations

from conman import utils
import os 

def init() -> int:
    # Check if .conman-config.yml already exists in current directory
    if os.path.isfile(".conman-config.yml"):
        print("Warning : .conman-config.yml already exists in current directory")
        print("Run : 'conman clean' to remove it first or 'conman init --force' to overwrite it")
    else:
        utils.cp_template_file(template_filename="empty_template_.conman-config.yml")
    return 0


    
if __name__ == "__main__":
    init()
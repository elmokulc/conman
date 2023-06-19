from __future__ import annotations

import os.path
import pkg_resources
from conman import utils
 

def init () -> int:
    utils.cp_template_file(template_filename="empty_template_.conman-config.yml")
    return 0


    
if __name__ == "__main__":
    init()
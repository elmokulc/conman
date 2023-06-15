
import os 

def getAttributes(clazz):
    return {name: attr for name, attr in clazz.__dict__.items()
            if not name.startswith("__") 
            and not callable(attr)
            and not type(attr) is staticmethod}


class Commands:
    def __init__(self):
        # Private attributes
        self.__CMDS_dict__ = {"init": self.init, 
                            "clean": self.clean,
                            "status": self.status,
                          }
        self.wdir = os.getcwd()
        
    def init(self):
        print("Fonction init() exécutée")
        
        
    def clean(self):
        print("Fonction clean() exécutée")
        
    def status(self):
        print(getAttributes(self))
        

                                

        
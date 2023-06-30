import conman as cn 
import os 

def test_init():
    cn.commands.init.init()
    # check is file .conman-config.yml exists in current directory
    assert os.path.isfile(".conman-config.yml")
    
def test install():
    cn.commands.install.install()
    # check if container is running
    assert cn.commands.status.status() == 'running'
    
if __name__ == "__main__":
    test_init()
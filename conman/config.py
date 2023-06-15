import yaml


def load_config(fpath):
    with open(fpath, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config
    
if __name__ == "__main__":
    config = load_config(fpath="./templates/conman-config.yml")
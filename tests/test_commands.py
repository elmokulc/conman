import conman as cn
import os


class TestInit:
    def test_init_file_creation(self):
        cn.commands.init.init()
        # check is file .conman-config.yml exists in current directory
        assert os.path.isfile(".conman-config.yml")

    def test_init_file_validity(self):
        assert not cn.commands.install.install().check_config_file()


class TestInstall:
    pass


if __name__ == "__main__":
    config = cn.commands.install.install()
    out = cn.commands.install.install_docker_compose(config)

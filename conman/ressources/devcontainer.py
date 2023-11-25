from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict, Any
from pathlib import Path
from conman.io import asi, Builder, create_directory, check_file_exist
from conman.utils import get_random_hash_str
from conman.constants import CONFIG_DIR, CONFIG_DIRNAME


@asi
@dataclass
class VSCode(Builder):
    settings: Dict[str, Any] = field(
        default_factory=lambda: {
            "terminal.integrated.defaultProfile.linux": "bash",
            "terminal.integrated.profiles.linux": {
                "bash (container default)": {
                    "path": "/bin/bash",
                    "overrideName": True,
                }
            },
        }
    )
    extensions: List[str] = field(
        default_factory=lambda: [
            "ms-python.python",
            "ms-python.vscode-pylance",
        ]
    )
    _optional_attributes_: List[str] = field(
        default_factory=lambda: ["settings", "extensions"]
    )


@asi
@dataclass
class Customizations(Builder):
    vscode: VSCode = VSCode()

    __private_class_lib__: Dict = field(
        default_factory=lambda: {"vscode": VSCode}
    )


@asi
@dataclass
class DevContainer(Builder):
    overrideCommand: bool = True
    name: str = "devcontainer_name"
    workspaceFolder: str = "/workspace/"
    dockerComposeFile: str = str(Path("./docker-compose.yml"))
    service: str = "main"
    shutdownAction: str = "stopCompose"
    customizations: Customizations = Customizations()
    initializeCommand: str = f"cd {CONFIG_DIR}scripts && /bin/bash initializeCommand.sh"
    onCreateCommand: str = (
        f"cd {workspaceFolder}{CONFIG_DIRNAME}/scripts && /bin/bash onCreateCommand.sh"
    )
    updateContentCommand: str = f"cd {workspaceFolder}{CONFIG_DIRNAME}/scripts && /bin/bash updateContentCommand.sh"
    postCreateCommand: str = f"cd {workspaceFolder}{CONFIG_DIRNAME}/scripts && /bin/bash postCreateCommand.sh"
    postStartCommand: str = (
        f"cd {workspaceFolder}{CONFIG_DIRNAME}/scripts && /bin/bash postStartCommand.sh"
    )

    _optional_attributes_: List[str] = field(
        default_factory=lambda: [
            "overrideCommand",
            "name",
            "dockerComposeFile",
            "service",
            "shutdownAction",
            "initializeCommand",
            "onCreateCommand",
            "updateContentCommand",
            "postCreateCommand",
            "postStartCommand",
        ]
    )

    __private_class_lib__: Dict = field(
        default_factory=lambda: {
            "customizations": Customizations,
            "vscode": VSCode,
        }
    )

    def dump_devcontainerjson_file(self, filename: str = "devcontainer.json"):
        self.dump_to_json(
            filename,
            rm_private=True,
            rm_optional=False,
            rm_empty=False,
            rm_none=True,
        )

    def dump_envFile(self, username, filename: str = "../.env"):
        hash_value = get_random_hash_str()
        VAR = f"COMPOSE_PROJECT_NAME={username}-{hash_value}"

        open(filename, "w").write(VAR)

    def empty_shell_script(self, filename, header: str = ""):
        create_directory(filename)
        if not check_file_exist(filename):
            shebang = "#!/bin/bash"
            header = "# " + header if not header.startswith("#") else header
            header = header + "\n" if not header.endswith("\n") else header
            content = (
                shebang
                + "\n"
                + header
                + "\n" * 2
                + "# <Write your commands here>"
            )
            open(filename, "w").write(content)
        else:
            print(f"Warning: {filename} already exists")
            print("Skipping...")

    def dump_postCreateCommand_script(
        self, filename: str = CONFIG_DIR + "scripts/" + "postCreateCommand.sh"
    ):
        self.empty_shell_script(filename, header="Post create command")

    def dump_initializeCommand_script(
        self, filename: str = CONFIG_DIR + "scripts/" + "initializeCommand.sh"
    ):
        self.empty_shell_script(filename, header="Initialize command")

    def dump_onCreateCommand_script(
        self, filename: str = CONFIG_DIR + "scripts/" + "onCreateCommand.sh"
    ):
        self.empty_shell_script(filename, header="On create command")

    def dump_updateContentCommand_script(
        self,
        filename: str = CONFIG_DIR + "scripts/" + "updateContentCommand.sh",
    ):
        self.empty_shell_script(filename, header="Update content command")

    def dump_postStartCommand_script(
        self, filename: str = CONFIG_DIR + "scripts/" + "postStartCommand.sh"
    ):
        self.empty_shell_script(filename, header="Post start command")

    def dump_optionals_scripts(self):
        self.dump_initializeCommand_script()
        self.dump_onCreateCommand_script()
        self.dump_updateContentCommand_script()
        self.dump_postStartCommand_script()
        self.dump_postCreateCommand_script()


if __name__ == "__main__":
    devcontainer = DevContainer()
    devcontainer.dump_devcontainerjson_file(filename="devcontainer.json")

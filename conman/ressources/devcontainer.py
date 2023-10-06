from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict, Any
from pathlib import Path
from conman.io import asi, Builder
from conman.utils import get_random_hash_str


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
    initializeCommand: str = "echo 'Initializing devcontainer...'"
    dockerComposeFile: str = str(Path("./docker-compose.yml"))
    service: str = "main_service_name"
    workspaceFolder: str = "/workspace"
    shutdownAction: str = "stopCompose"
    customizations: Customizations = Customizations()
    postCreateCommand: str = "echo 'Post create command...'"
    postStartCommand: str = "echo 'Post start command...'"

    _optional_attributes_: List[str] = field(
        default_factory=lambda: [
            "overrideCommand",
            "name",
            "initializeCommand",
            "dockerComposeFile",
            "service",
            "shutdownAction",
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
            rm_none=False,
        )

    def dump_envFile(self, username, filename: str = "../.env"):
        hash_value = get_random_hash_str()
        VAR = f"COMPOSE_PROJECT_NAME={username}-{hash_value}"

        open(filename, "w").write(VAR)


if __name__ == "__main__":
    devcontainer = DevContainer()
    devcontainer.dump_devcontainerjson_file(filename="devcontainer.json")

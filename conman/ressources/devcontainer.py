from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict, Any
from pathlib import Path
from conman.io import asi, Builder


@asi
@dataclass
class VSCode(Builder):
    settings: Dict[str, Any] = field(default_factory=lambda: {})
    extensions: List[str] = field(
        default_factory=lambda: [
            "ms-python.python",
            "ms-python.vscode-pylance",
        ]
    )
    _optional_attributes_: List[str] = field(
        default_factory=lambda: [
            "settings",
        ]
    )


@asi
@dataclass
class Customizations(Builder):
    vscode: VSCode = field(default_factory=VSCode)


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
    customizations: Customizations = field(default_factory=Customizations)
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
            rm_empty=True,
            rm_none=True,
        )


if __name__ == "__main__":
    devcontainer = DevContainer()
    devcontainer.dump_to_json(filename="devcontainer.json")

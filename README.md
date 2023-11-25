# **CON**tainer **MAN**ager : conman
---

## Description

Conman is a tool to manage containers. It is designed to be used with docker, docker-compose et VScode devcontainer tool.

---

## Requirements 

- Unix (Linux, macOS) based operating system (WSL workaround for Windows)
- A container engine ans its composer tool: 
  - [Docker 24.0+](https://docs.docker.com/get-docker/) and [Docker-compose 2.20+](https://docs.docker.com/compose/)
  - [Podman 4.0+](https://podman.io/getting-started/installation) and [Podman-compose 1.0.6+](https://docs.podman.io/en/latest/markdown/podman-compose.1.html)
- [Python 3.8+](https://www.python.org/downloads/)
- Python modules :
    - [pip 21.0.1+](https://pip.pypa.io/en/stable/installation/) (Need setuptools integration)
    - [pyyaml 5.4.1+](https://pypi.org/project/PyYAML/)
---

## Installation

- Install conman using pip:

    ```bash
    pip install conman-tool
    ```

    You can also install conman from source, tcd he current stable realease is `1.2.0`:

    ```bash
    pip install git+https://github.com/elmokulc/conman.git@1.2.0
    ```

---

## Usage
### When starting a new project
- Go to you project directory:

    ```bash
        mkdir my_project
        cd my_project
    ```
- Create a conman configuration file by running:

    ```bash
    conman init
    ```

    This will create a directory named `.conman` within the configuration file `conman-config.yml`.

    ```bash
    $ ➜ ~/my_project $ conman init
    $ ➜ ~/my_project $ tree -a
    .
    └── .conman
        └── conman-config.yml

    1 directory, 1 file
    ```
- Edit the `conman-config.yml` configuration file to fit your needs.

As example:

```yml 
# Images Settings
images:
    root:
        generate: true
        name: BigFoot
        tag: latest
        from_image:
            name: ubuntu
            tag: '20.04'
        conda_environment:
            directory: /opt/conda
            env_name: myenv
            environment_file: ./environment.yml
        extra_instructions: 
            - "RUN echo 'export $PYTHONPATH=/python_modules:$PYTHONPATH' >> ~/.bashrc"
    user:
        extra_instructions:
            - "RUN sudo mkdir -p /python_modules"
            - "RUN sudo chown -R $USER:$USER /python_modules"
            - "RUN echo 'export $PYTHONPATH=/python_modules:$PYTHONPATH' >> ~/.bashrc"     

# Container Settings
container:
    engine: docker # docker or podman
    compose:
        service_name: main
        volumes:
        - ..:/workspace
        - path_module1/module1:/python_modules/module1
        - path_module2/module2:/python_modules/module2
    devcontainer:
        customizations:
            vscode:
                settings: {}
                extensions:
                - ms-python.python
                - ms-python.vscode-pylance
                - ms-toolsai.jupyter
    graphical:
        protocol: x11
    gpu:
        manufacturer: nvidia
        count: 1
```

- By running: 
    
    ```bash
    conman build
    ```

    Conman will generate a `docker-compose.yml` file and a `Dockerfile.user`, enventually: a `.devcontainer` directory within a `devcontainer.json` file, a `Dockerfile.root` and a conda `environment.yml` file, all of this according to your configuration file: `.conman-config.yml` .

    Here is an example of the output from the previous configuration file:

    ```console
    $ ➜ ~/my_project $ conman build
        Building...
        Directory .devcontainer created
        Creating devcontainer.json file...
        Executing xhost +local: ...
        Appending volumes for display configuration...
        -> Add volume: /tmp/.X11-unix:/tmp/.X11-unix:rw
        -> Add volume: /home/vscode/.Xauthority:/home/vscode/.Xauthority:rw
        -> Display forwading activated
        -> Add volume: ..:/workspace
        -> Add volume: path_module1/module1:/python_modules/module1
        -> Add volume: path_module2/module2:/python_modules/module2
        -> GPU activated
        --- Build user Dockerfile ---
        Adding user extra instructions to Dockerfile...
        Generated Dockerfile.user at:    ~/my_project/.devcontainer/Dockerfile.user
        --- Build root Dockerfile ---
        Creating conda env file at:     ~/my_project/.conman/environment.yml
        Adding root extra instructions to Dockerfile...
        Generated Dockerfile.root at:    ~/my_project/.conman/Dockerfile.root
        Project Building done successfully
    ```
    The project directory will now look like this:
    ```console
    $ ➜ ~/my_project $ tree -a
    .
    ├── .conman
    │   ├── conda
    │   │   └── environment.yml
    │   ├── conman-config.yml
    │   └── scripts
    │       ├── initializeCommand.sh
    │       ├── onCreateCommand.sh
    │       ├── postCreateCommand.sh
    │       ├── postStartCommand.sh
    │       └── updateContentCommand.sh
    ├── .devcontainer
    │   ├── build_root_img.sh
    │   ├── devcontainer.json
    │   ├── docker-compose.yml
    │   ├── Dockerfile.root
    │   └── Dockerfile.user
    └── .env

    4 directories, 13 files 
    ``` 
### When working on an existing project

In case you want to work on an existing project, you can use the `conman update` command by running:

```bash
conman update
```

This command will regenerate user dependant files such as `Dockerfile.user`, `docker-compose.yml` or `devcontainer.json`:

```console
$ ➜ ~/my_project $ conman update
Updating conman build...
Creating devcontainer.json file...
[...]
Appending volumes for display configuration...
-> Add volume: /tmp/.X11-unix:/tmp/.X11-unix:rw
-> Add volume: /home/vscode/.Xauthority:/home/vscode/.Xauthority:rw
-> Display forwading activated
-> Add volume: ../:/workspace
--- Build user Dockerfile ---
Adding conda environment to Dockerfile...
No extra instructions in user image
Generated Dockerfile.user at:    /workspaces/conman/myproject/.devcontainer/Dockerfile.user
```

## Help

  All available commands can be listed by running:

```bash
conman --help
```

if you need some details about a specific command, you can run:

```bash
conman <command> --help
```

---

## Root image generation

In case you need to generate a root image, conman will generate a build script for you name `build_root_img.sh` in the same folder that `Dockerfile.root`.
Unfortunalety, you will need to set execution permissions and run this script manually.

To set proper permissions and run the script:

```bash
    chmod +x build_root_img.sh && ./build_root_img.sh
```

## Troubleshoting

- According to your system configuration and yours permissions, the location of the entry point of conman may change.
You may need to update your `$PATH` variable.

    The command:

    ```bash
    pip show conman
    ```
    
    will give you the following output within the location of the conman package:
    ```console hl_lines="1"
        Name: conman
        Version: [****]
        Summary: [****]
        Home-page: [****]
        Author: [****]
        Author-email: [****]
        License: [****]
        Location: /home/<username>/.local/lib/python3.8/site-packages
        Editable project location: [****]
        Requires: [****]
    ```
    In this example, the location of the entrypoint to be add will be `/home/<username>/.local/bin`.

    You can then add the following line to your `.bashrc` or `.zshrc` file:

    ```bash
    export PATH=$PATH://home/$USER/.local/bin
    ```

    or by running:

    ```bash
    echo 'export PATH=$PATH:/home/'$USER'/.local/bin' >> ~/.bashrc
    ```


    This will add the conman executable to your `$PATH` variable.

## Contributing

If you want to contribute to this project, please read the [CONTRIBUTING.md](CONTRIBUTING.md) file.
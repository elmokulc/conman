# **CON**tainer **MAN**ager : conman
---

## Description

Conman is a tool to manage containers. It is designed to be used with docker, docker-compose et VScode devcontainer tool.

---

## Requirements 

- Unix (Linux, macOS) based operating system (WSL workaround for Windows)
- [Docker 24.0+](https://docs.docker.com/get-docker/) and [Docker-compose 2.20+](https://docs.docker.com/compose/)
- [Python 3.8+](https://www.python.org/downloads/)
- Python modules :
    - [pip 21.0.1+](https://pip.pypa.io/en/stable/installation/) (Need setuptools integration)

---

## Installation

- Install conman using pip:

    ```bash
    pip install git+https://github.com/elmokulc/conman.git@0.0.1
    ```

    **NB**: Replace `<branch_name>` by the name of the branch you want to install.

    The current stable realease is `1.0`:

    ```bash
    pip install git+https://github.com/elmokulc/conman.git@1.0
    ```

---

## Usage

- Go to you project directory:

    ```bash
        mkdir my_project
        cd my_project
    ```
- Create a conman configuration file by running:

    ```bash
    conman init
    ```

    This will create a file named `.conman-config.yml` in your project directory.

    ```bash
    $ ➜ ~/my_project $ conman init
    $ ➜ ~/my_project $ tree -a
    .
    └── .conman-config.yml

    0 directories, 1 file
    ```
- Edit the `.conman-config.yml` configuration file to fit your needs.

As example:

```yml 
# Images Settings
images:
    root:
        generate: false
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
    docker_compose:
        container_name: ContainerNameDockerCompose
        service_name: main_service_name
        volumes:
        - ..:/workspace
        - path_module1/module1:/python_modules/module1
        - path_module2/module2:/python_modules/module2
    devcontainer:
        name: devcontainer_name
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
        Creating conda env file at:     ./environment.yml
        Adding root extra instructions to Dockerfile...
        Generated Dockerfile.root at:    ~/my_project/.devcontainer/Dockerfile.root
        Project Building done successfully
    ```
    The project directory will now look like this:
    ```console
    $ ➜ ~/my_project $ tree -a
        .
        ├── .conman-config.yml
        ├── .devcontainer
        │   ├── devcontainer.json
        │   ├── docker-compose.yml
        │   ├── Dockerfile.root
        │   └── Dockerfile.user
        └── environment.yml

        1 directory, 6 files  
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
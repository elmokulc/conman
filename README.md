# **CON**tainer **MAN**ager : conman
---

## Description

Conman is a tool to manage containers. It is designed to be used with docker, docker-compose et VScode devcontainer tool.

---

## Requirements 

- Unix (Linux, macOS) based operating system (WSL workaround for Windows)
- Docker and Docker-compose
- Python 3.8+
- Python modules :
    - pip 21.0.1+ (Need setuptools integration)

---

## Installation

- Install conman using pip:

    ```bash
    pip install git+https://github.com/elmokulc/conman.git@<branch_name>
    ```

    **NB**: Replace `<branch_name>` by the name of the branch you want to install. The current most advanced branch is `0.0.2`.

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
        name: root_img_name
        tag: root_img_tag
        from_image:
            name: ubuntu
            tag: '20.04'
        conda_environment:
            enabled: true
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

# User_settings Settings
user_settings:
    volumes: 
        - ..:/workspace
        - path_module1/module1:/python_modules/module1
        - path_module2/module2:/python_modules/module2

# Container Settings
container:
    name: compose_img_name
    main_service:
        name: main_container
        container_name: container_stack_name
    devcontainer:
        enabled: true
        name: devcontainer_name
        extensions: 
            - "ms-python.python"
            - "ms-python.vscode-pylance"
    graphical:
        enabled: false
        protocol: x11
    gpu:
        enabled: false
        manufacturer: nvidia
        count: 1
```

- By running: 
    
    ```bash
    conman build
    ```

    Conman will generate a `docker-compose.yml` file and a `Dockerfile-user`, enventually: a `.devcontainer` directory within a `devcontainer.json` file, a `Dockerfile` and a conda `environment.yml` file, all of this according to your configuration file: `.conman-config.yml` .

    Here is an example of the output from the previous configuration file:

    ```console
    $ ➜ ~/my_project $ conman build
    Checking config file ...
    base_name = ubuntu:20.04
    volumes:
    - .:/workspace
    conda direcotry = /opt/conda
    conda env name = myenv
    Executing xhost +local: ...
    Directory .devcontainer created
    Extra instructions found. Adding them to Dockerfile
    Adding:         RUN sudo mkdir -p /python_modules
    Adding:         RUN sudo chown -R $USER:$USER /python_modules
    Adding:         RUN echo 'export $PYTHONPATH=/python_modules:$PYTHONPATH' >> ~/.bashrc
    Generated Dockerfile-user at:    /home/vscode/my_project/.devcontainer/Dockerfile-user
    Conda env file exists at:       ./environment.yml
    Extra instructions found. Adding them to Dockerfile-user
    Adding:         RUN echo 'export $PYTHONPATH=/python_modules:$PYTHONPATH' >> ~/.bashrc
    Generated Dockerfile at:         /home/vscode/my_project/Dockerfile
    ```
    The project directory will now look like this:
    ```console
    $ ➜ ~/my_project $ tree -a
    .
    ├── .conman-config.yml
    ├── .devcontainer
    │   ├── devcontainer.json
    │   ├── docker-compose.yml
    │   └── Dockerfile-user
    ├── Dockerfile
    └── environment.yml


        1 directory, 6 files   
    ``` 

- NB:  All available commands can be listed by running:

    ```bash
    conman --help
    ```
---

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

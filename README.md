# **CON**tainer **MAN**ager : conman
---

## Description

Conman is a tool to manage containers. It is designed to be used with docker, docker-compose et VScode devcontainer tool.

---

## Requirements 

- Unix (Linux, macOS) based operating system (WSL workaround for Windows)
- Docker and Docker-compose
- Python 3.6+
- Python modules :
    - pip 21.0.1+ (Need setuptools integration)

---

## Installation

- Install conman using pip:

    ```bash
    pip install git+https://github.com/elmokulc/conman.git@<branch_name>
    ```

    **NB**: Replace `<branch_name>` by the name of the branch you want to install. The current most advanced branch is `dev`.

- According to your system configuration and yours permissions, the location of the entry point of conman may change.
You may need variable to update your `$PATH` variable.

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
    export PATH=$PATH://home/<username>/.local/bin
    ```

    or by running:

    ```bash
    echo 'export PATH=$PATH:/home/<username>/.local/bin' >> ~/.bashrc
    ```


    This will add the conman executable to your `$PATH` variable.

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
root_image:
    generate: true
    name: "ubuntu"
    tag: "20.04"
    conda:
        enabled: true
        directory: "/opt/conda"
        env_name: "myenv"
        environment_file: "environment.yml"  

volumes:
    - .:/workspace

graphical:
    enabled: true
    protocol: "x11"

gpu:
    enabled: true
    manufacturer: "nvidia"
    count: 1

container:
    name: "compose_img_name"
    main_service:
        name: "main_container"
        container_name: "your_container_name"
    devcontainer:
        enabled: true
        name: "your_devcontainer_name"
        extensions:
            - "ms-python.python"
            - "ms-python.vscode-pylance"
```

- By running: 
    
    ```bash
    conman install
    ```

    Conman will generate a `docker-compose.yml` file and a `Dockerfile-user`, enventually both a `.devcontainer` directory within a `devcontainer.json` file and a `Dockerfile` according to your configuration file.

    Here is an example of the output from the previous configuration file:

    ```console
    $ ➜ ~/my_project $ conman install
    Checking config file ...
    base_name = ubuntu:20.04
    volumes:
    - .:/workspace
    conda direcotry = /opt/conda
    conda env name = myenv
    Executing xhost +local: ...
    Directory .devcontainer created
    $ ➜ ~/my_project $ tree -a
    .
    ├── .conman-config.yml
    ├── .devcontainer
    │   ├── devcontainer.json
    │   ├── docker-compose.yml
    │   └── Dockerfile-user
    └── Dockerfile

        1 directory, 5 files   
    ``` 

- NB:  All available commands can be listed by running:

    ```bash
    conman --help
    ```
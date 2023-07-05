# **CON**tainer **MAN**ager : conman
---

## Description

Conman is a tool to manage containers. It is designed to be used with docker, docker-compose et VScode devcontainer tool.

---

## Requirements 

- Unix (Linux, macOS) based operating system (WSL workaround for Windows)
- Python 3.6+
- Python modules :
    - pip

---

## Installation

- Install conman using pip:

    ```bash
    pip install git+https://github.com/elmokulc/conman.git@<branch_name>
    ```

    **NB**: Replace `<branch_name>` by the name of the branch you want to install. The current most advanced branch is 'dev'.

- According to your sys 

---

## Usage
- Go to your project directory and create a conman configuration file by running:

    ```bash
    conman init
    ```

    This will create a file named `.conman-config.yml` in your project directory.

- Edit the configuration file to fit your needs.
- By running: 
    
    ```bash
    conman install
    ```

    Conman will generate a `docker-compose.yml` file and a `Dockerfile-conman`, enventually a `.devcontainer` directory within a `devcontainer.json` file according to your configuration file.
    

- NB:  All available commands can be listed by running:

    ```bash
    conman --help
    ```
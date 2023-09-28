import os


def manage_conda_env_file(
    envfile,
    conda_env_name,
    pip_packages=["scipy", "opencv-python", "opencv-contrib-python"],
    conda_packages=["python=3.8", "pip", "numpy"],
    channels=["conda-forge", "anaconda", "defaults"],
):
    """_summary_
    Manage conda environment.yml file
    if file exists do nothing else create an empty file
    Args:
        envfile (str): environment.yml file path
    """

    if not os.path.isfile(envfile):
        print(f"Creating conda env file at: \t{envfile}")
        open(envfile, "w").write("name: " + conda_env_name + "\n")
        open(envfile, "a").write("channels: \n")
        for channel in channels:
            open(envfile, "a").write("  - " + channel + "\n")
        open(envfile, "a").write("dependencies: \n")
        for conda_package in conda_packages:
            open(envfile, "a").write("  - " + conda_package + "\n")
        open(envfile, "a").write("  - pip: \n")
        for pip_package in pip_packages:
            open(envfile, "a").write("    - " + pip_package + "\n")
    else:
        print(f"Conda env file exists at: \t{envfile}")


class Instructions:
    """
    Represents an instruction in a Dockerfile.
    """

    @classmethod
    def from_line(cls, line: str, comments: str = ""):
        cmd = line.split(" ")[0]
        args = " ".join(line.split(" ")[1:])
        return cls(cmd, args, comments)

    @classmethod
    def from_lines(cls, lines: str, comment: str = ""):
        cmds = []
        argss = []
        for line in lines:
            cmds.append(line.split(" ")[0])
            argss.append(" ".join(line.split(" ")[1:]))
        return cls(cmds, argss, comment)

    def __init__(self, cmds, arguments, comments=""):
        """
        Initialize the Instructions object.

        Args:
            cmds (str or list): The command(s) of the instruction.
            arguments (str or list): The argument(s) of the instruction.
            comments (str, optional): Comments for the instruction. Defaults to "".
        """
        self.cmds = cmds
        self.arguments = arguments

        self.comments = (
            "# " + comments
            if comments and not comments.startswith("#")
            else comments
        )

    def generate(self):
        """
        Generate the instruction as a string.

        Returns:
            str: The generated instruction string.
        """
        if isinstance(self.cmds, list):
            output = ""
            for ind, argument in enumerate(self.arguments):
                if ind == 0:
                    output += f"{self.comments}\n{self.cmds[ind]} {argument}\n"
                else:
                    output += f"{self.cmds[ind]} {argument}\n"
            return output + "\n"

        elif isinstance(self.arguments, list) and not isinstance(
            self.cmds, list
        ):
            output = ""
            for ind, argument in enumerate(self.arguments):
                if ind == 0:
                    output += f"{self.comments}\n{self.cmds} {argument}\n"
                else:
                    output += f"{self.cmds} {argument}\n"
            return output + "\n"
        else:
            return f"{self.comments}\n{self.cmds} {self.arguments}\n\n"


class DockerFile:
    """
    A class representing a Dockerfile.

    Attributes:
        instructions (list): The list of instructions in the Dockerfile.

    Methods:
        __init__(self)
            Initializes a new instance of the DockerFile class.

        add(self, cmds, arguments, comments="")
            Adds a new instruction to the Dockerfile.

        generate(self, filename)
            Generates the Dockerfile content and writes it to a file.

    """

    def __init__(self):
        """
        Initializes a new instance of the DockerFile class.

        Returns:
            None
        """

        self.instructions = []

    def add(self, cmds, arguments, comments=""):
        """
        Adds a new instruction to the Dockerfile.

        Args:
            cmds (str): The command of the instruction.
            arguments (str): The arguments of the instruction.
            comments (str): Optional comments for the instruction.

        Returns:
            None
        """

        self.instructions.append(Instructions(cmds, arguments, comments))

    def add_line(self, line, comments=""):
        """
        Adds a new instruction to the Dockerfile.

        Args:
            line (str): The line of the instruction.

        Returns:
            None
        """

        cmd = line.split(" ")[0]
        args = " ".join(line.split(" ")[1:])
        self.instructions.append(Instructions(cmd, args, comments))

    def add_instruction(self, instruction: Instructions):
        """
        Adds a new instruction to the Dockerfile.
        Args:
            instruction (Instructions): The instruction to add.
        Returns:
            None
        """
        self.instructions.append(instruction)

    def closing_file(self):
        self.add(
            cmds=["SHELL", "ENTRYPOINT"],
            arguments=['["/bin/bash", "--login", "-c"]', '["/bin/bash"]'],
            comments="Closing file",
        )
        return self

    def generate(self, filename):
        """
        Generates the Dockerfile content and writes it to a file.

        Args:
            filename (str): The filename of the generated Dockerfile.

        Returns:
            None
        """

        with open(filename, "w") as file:
            file.writelines(
                instruction.generate() for instruction in self.instructions
            )
        print(f"Generated {filename.split('/')[-1]} at: \t {filename}")

    def default_debian_root_instruction(
        self, base_image: str = "ubuntu:20.04", conda_obj: object = None
    ):
        self.add(
            "FROM",
            f"{base_image}",
            comments="Source image",
        )

        # Set Debian frontend to noninteractive
        self.add("ENV", 'DEBIAN_FRONTEND="noninteractive" TZ="Europe/Paris"')

        # Add basics libraries
        self.add("RUN", "apt-get update", comments="Updating apt cache")

        self.add(
            "RUN",
            "apt-get install -y build-essential cmake libncurses5-dev libncursesw5-dev libv4l-dev libxcursor-dev libxcomposite-dev libxdamage-dev libxrandr-dev libxtst-dev libxss-dev libdbus-1-dev libevent-dev libfontconfig1-dev libcap-dev libpulse-dev libudev-dev libpci-dev libnss3-dev libasound2-dev libegl1-mesa-dev",
            comments="Development Tools and Libraries",
        )

        self.add(
            "RUN", "apt-get install -y ffmpeg", comments="Multimedia libraries"
        )

        self.add(
            "RUN",
            "apt-get update && apt-get install -y x11-apps xauth",
            comments="X11 libraries",
        )

        self.add(
            "RUN",
            "apt-get install -y git wget sudo gperf bison nodejs htop",
            comments="Other libraries",
        )

        self.add(
            "RUN",
            [
                "apt install locales",
                "locale-gen en_US.UTF-8",
                "dpkg-reconfigure locales",
            ],
            comments="Locales update",
        )

        self.add("RUN", "apt-get clean", comments="Cleaning apt cache")

        # Conda settings and installation
        if conda_obj:
            # Add conda arguments
            self.add(
                "ARG",
                [
                    f"CONDA_DIRECTORY={conda_obj.directory}",
                    f"CONDA_ENV_NAME={conda_obj.env_name}",
                ],
                comments="CONDA ARGS",
            )

            # Define conda environment variables
            self.add(
                "ENV",
                [
                    "CONDA_DIRECTORY $CONDA_DIRECTORY",
                    "CONDA_ENV_NAME $CONDA_ENV_NAME",
                    "CONDA_BIN_PATH $CONDA_DIRECTORY/condabin/conda",
                    "CONDA_ENV_BIN_PATH $CONDA_DIRECTORY/envs/$CONDA_ENV_NAME/bin",
                    "CONDA_ENV_PATH $CONDA_DIRECTORY/envs/$CONDA_ENV_NAME",
                ],
                comments="Conda environment variables",
            )

            # Add conda executable to PATH

            self.add(
                "ENV",
                "PATH $CONDA_DIRECTORY/condabin/:$PATH",
                comments="Add conda executable to PATH",
            )

            # Setting umask to 0000

            self.add(
                "RUN",
                [
                    'line_num=$(cat /etc/pam.d/common-session | grep -n umask | cut -d: -f1 | tail -1) && \ \n\tsed -i "${line_num}s/.*/session optional pam_umask.so umask=000/" /etc/pam.d/common-session',
                    'line_num=$(cat /etc/login.defs | grep -n UMASK | cut -d: -f1 | tail -1) && \ \n\tsed -i "${line_num}s/.*/UMASK               000/" /etc/pam.d/common-session',
                    "echo 'umask 000' >> ~/.profile",
                ],
                comments="Setting umask",
            )

            # Installing miniconda
            self.add(
                "RUN",
                "umask 000 && \ \n\tmkdir -p ${CONDA_DIRECTORY} && \ \n\tchmod 777 ${CONDA_DIRECTORY} && \ \n\twget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \ \n\tbin/bash ~/miniconda.sh -ub -p $CONDA_DIRECTORY && \ \n\trm ~/miniconda.sh",
                comments="Installing miniconda",
            )

            manage_conda_env_file(
                conda_obj.environment_file, conda_obj.env_name
            )

            self.add(
                ["COPY", "RUN"],
                [
                    f"{conda_obj.environment_file} /tmp/environment.yml",
                    "umask 000 && \ \n\tconda update -n base conda && \ \n\tconda create -y -n $CONDA_ENV_NAME && \ \n\tconda env update --name $CONDA_ENV_NAME --file /tmp/environment.yml --prune ",
                ],
                comments="Conda env creation",
            )

            self.add(
                "RUN",
                [
                    'echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc',
                    'echo "conda activate $CONDA_ENV_NAME" >> ~/.bashrc',
                ],
                comments="Conda env activation for root user",
            )

    def default_user_instruction(
        self,
        base_name: str = "userImgName:userImgTag",
        graphical: bool = False,
        conda_obj: object = None,
    ):

        self.add("ARG", f"BASE_IMAGE={base_name}", comments="ARG BASE_IMAGE")
        self.add("FROM", "${BASE_IMAGE}", comments="FROM ${BASE_IMAGE}")
        self.add(
            "ARG",
            ["USER_NAME", "USER_UID", "USER_GID"],
            comments="ARGS",
        )
        self.add(
            "ENV",
            [
                "USER_NAME=${USER_NAME}",
                "USER_GID=${USER_GID}",
                "USER_UID=${USER_UID}",
            ],
            comments="ENV VARIABLES",
        )

        if graphical:
            self.add(
                ["ARG", "ENV"],
                ["DISPLAY", "DISPLAY=${DISPLAY}"],
                comments="ARGS GRAPHICAL",
            )

            self.add(
                "RUN",
                "apt-get update \\ \n && apt-get install -y sudo x11-apps xauth",
            )

        self.add(
            "RUN",
            [
                f"mkdir -p /etc/sudoers.d",
                f"groupadd --gid $USER_GID $USER_NAME \\ \n    && useradd --uid $USER_UID --gid $USER_GID -m $USER_NAME",
                f"echo $USER_NAME ALL=\\(root\\) NOPASSWD:ALL > /etc/sudoers.d/$USER_NAME \\ \n   && chmod 0440 /etc/sudoers.d/$USER_NAME",
                "usermod -a -G root ${USER_NAME}",
            ],
            comments="USER CREATION",
        )
        self.add(
            "USER", f"${{USER_UID}}:${{USER_GID}}", comments="Log as $USER"
        )

        # Conda settings and installation
        if conda_obj:
            self.add(
                ["ARG", "ENV", "ENV"],
                [
                    "CONDA_ENV_NAME",
                    "CONDA_ENV_NAME=${CONDA_ENV_NAME}",
                    "CONDA_ENV_PATH=/opt/conda/envs/${CONDA_ENV_NAME}/bin/",
                ],
                comments="CONDA ARGS AND ENV VARIABLES",
            )

            self.add(
                "RUN",
                [
                    'echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc',
                    'echo "conda activate $CONDA_ENV_NAME" >> ~/.bashrc',
                ],
                comments="Intialize conda and activate conda environment",
            )

    def default_user_end_instruction(self):
        self.add("RUN", "source ~/.bashrc")
        self.add("SHELL", ['["/bin/bash", "--login", "-c"]'])

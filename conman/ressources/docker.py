class DockerFile:
    def __init__(self):
        self.instructions = []

    def add_instruction(self, instruction):
        self.instructions.append(instruction)
        
    def add_group_instructions(self, cmd, instructions, comments=""):
        for instruction in instructions:
            self.instructions.append(Instruction(cmd, instruction, comments))

    def generate(self, filename):
        with open(filename, 'w') as file:
            for instruction in self.instructions:
                file.write(instruction.generate())

class Instruction:
    def __init__(self, cmd, arguments, comments=""):
        self.cmd = cmd
        self.arguments = arguments
        
        if not comments == "" and not comments.startswith("#"):
            self.comments = "# " + comments
        else:
            self.comments = comments
            
    def generate(self):
        return f"{self.comments}\n{self.cmd} {self.arguments}\n"

dockerfile = DockerFile()

# ARG BASE_IMAGE
dockerfile.add_instruction(Instruction("ARG", "BASE_IMAGE", comments="ARG BASE_IMAGE"))

# FROM ${BASE_IMAGE}
dockerfile.add_instruction(Instruction("FROM", "${BASE_IMAGE}", comments="FROM ${BASE_IMAGE}"))

# ARGS
dockerfile.add_group_instructions("ARG", 
            ["USER_NAME", "USER_UID",
             "USER_GID",
             "CONDA_ENV_NAME"],
            comments="ARGS")

# ENV VARIABLES
dockerfile.add_group_instructions("ENV",  
            ["USER_NAME=${USER_NAME}",
            "USER_GID=${USER_GID}",
            "USER_UID=${USER_UID}",
            "CONDA_ENV_NAME=${CONDA_ENV_NAME}",
            "CONDA_ENV_PATH=/opt/conda/envs/${CONDA_ENV_NAME}/bin/",
            "DISPLAY=${DISPLAY}"], 
            comments="ENV VARIABLES")

# USER CREATION
dockerfile.add_group_instructions("RUN",
                                  [f"groupadd --gid $USER_GID $USER_NAME \\ \n    && useradd --uid $USER_UID --gid $USER_GID -m $USER_NAME",
                                   f"echo $USER_NAME ALL=\\(root\\) NOPASSWD:ALL > /etc/sudoers.d/$USER_NAME \\ \n   && chmod 0440 /etc/sudoers.d/$USER_NAME",
                                   "cd / && mkdir python_packages",
                                   "usermod -a -G root ${USER_NAME}"
                                  ]
)


# Log as $USER and create a .bashrc file for config
dockerfile.add_instruction(Instruction("USER", f"${{USER_UID}}:${{USER_GID}}"))

# dockerfile.add_instruction(Instruction("RUN", f"echo \". ${CONDA_DIR}/etc/profile.d/conda.sh\" >> ~/.bashrc && \\"))
# dockerfile.add_instruction(Instruction("RUN", f"    echo \"conda activate $CONDA_ENV_NAME\" >> ~/.bashrc && \\"))
# dockerfile.add_instruction(Instruction("RUN", f"    echo \"export PYTHONPATH=\\$PYTHONPATH:/python_packages/\" >> ~/.bashrc && \\"))
# dockerfile.add_instruction(Instruction("RUN", f"    echo \"{CONDA_BIN_PATH} activate $CONDA_ENV_NAME\" >> ~/.bashrc"))

# dockerfile.add_instruction(Instruction("RUN", "echo \"export PYTHONPATH=\\$PYTHONPATH:/python_packages/\" >> ~/.bashrc"))

dockerfile.add_instruction(Instruction("SHELL", "[\"/bin/bash\", \"--login\", \"-c\"]"))
dockerfile.add_instruction(Instruction("RUN", "/bin/bash ~/.bashrc"))
dockerfile.add_instruction(Instruction("SHELL", "[\"/bin/bash\", \"--login\", \"-c\"]"))
dockerfile.add_instruction(Instruction("ENTRYPOINT", "[\"/bin/bash\"]"))

dockerfile.generate("Dockerfile")


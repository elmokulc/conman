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


class Instructions:
    """
    Represents an instruction in a Dockerfile.
    """

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

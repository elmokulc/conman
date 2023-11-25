from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict, Any
from pathlib import Path
import json
import yaml
import copy
import types


def create_directory(path: str) -> None:
    """
    Creates a directory if it does not already exist.

    Args:
        path (str): Privoded path, can be a path to a file or a directory.

    Returns:
        None
    """
    # Conversion to Path object
    path = Path(path)

    # Create directory if it does not exist
    if path.parent != Path():
        if not path.parent.exists():
            path.parent.mkdir(parents=True)


def check_file_exist(path: str) -> bool:
    """
    Check if a file exists.

    Args:
        path (str): Privoded path, can be a path to a file or a directory.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    # Conversion to Path object
    path = Path(path)

    # Check if file exists
    if path.exists():
        return True
    else:
        return False


def asi(subclass):
    """
    A decorator function that adds support for automatic super() initialization to a subclass.

    Args:
        subclass (class): The subclass to decorate.

    Returns:
        class: The decorated subclass.
    """

    original_init = subclass.__init__

    def new_init(self, *args, **kwargs):
        """
        Custom initialization method that automatically calls super().__init__().

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            None
        """

        super(subclass, self).__init__(*args, **kwargs)
        original_init(self, *args, **kwargs)

    subclass.__init__ = new_init
    return subclass


class Builder:
    def __init__(self, __private_class_lib__: Dict = {}, **kwargs) -> None:

        self.__private_class_lib__: Dict = __private_class_lib__

        for k, v in kwargs.items():
            setattr(self, k, v)

        self.class_register()

    @classmethod
    def from_dic(cls, dic):
        kwargs = {}

        for key, value in dic.items():
            temps_instance = cls()
            temps_instance.update_private_class_lib(dic)

            if (
                hasattr(temps_instance, "__private_class_lib__")
                and key in temps_instance.__private_class_lib__
            ):
                _class = temps_instance.__private_class_lib__[key]
            else:
                _class = Builder

            if value.__class__ == dict:
                sub_instance = _class()
                sub_instance.update_private_class_lib(dic)
                kwargs[key] = sub_instance.from_dic(value)
            else:
                kwargs[key] = value

        instance = cls(**kwargs)
        instance.update_private_class_lib(dic)
        return instance

    def update_private_class_lib(self, dic: Dict):
        inter_key = set(dic) & set(self.__private_class_lib__)
        shared_class_lib = {}
        for key in inter_key:
            shared_class_lib[key] = self.__private_class_lib__[key]

        self.__private_class_lib__ = shared_class_lib
        return self

    @staticmethod
    def class_representer(dumper, data):
        """
        A static method used as a custom YAML representer for Field objects.

        Args:
            dumper (yaml.Dumper): The YAML dumper object.
            data (Field): The Field object to represent.

        Returns:
            Any: The YAML representation of the Field object.
        """

        return dumper.represent_dict(data.__dict__)

    @classmethod
    def class_register(cls):
        """
        Registers the field_representer as a representer for the Field class in YAML.

        Returns:
            None
        """

        yaml.add_representer(cls, cls.class_representer)

    @staticmethod
    def deleting_attributes(obj: object, attributes: List[str]) -> object:
        for attr in attributes:
            delattr(obj, attr)
        return obj

    @staticmethod
    def remove_private_attributes(obj) -> None:
        attributes = obj.__dict__
        private_attributes = []
        for attr, value in attributes.items():
            if attr.startswith("__private_") or attr.startswith("_"):
                private_attributes.append(attr)
            elif hasattr(value, "__dict__"):
                obj.remove_private_attributes(value)

        Builder.deleting_attributes(obj, private_attributes)

        return obj

    @staticmethod
    def remove_empty_attributes(obj):
        # Get all attributes of the object
        attributes = obj.__dict__

        # Iterate through attributes and remove empty ones
        empty_attributes = []
        for attr, value in attributes.items():
            if isinstance(value, (list, dict)):
                # Case where the attribute is a list or a dictionary
                if not value:
                    empty_attributes.append(attr)
            elif hasattr(value, "__dict__"):
                # Case where the attribute is an instance of a class
                obj.remove_empty_attributes(value)
                if not value.__dict__:
                    empty_attributes.append(attr)
            elif not value:
                # General case where the attribute is empty
                empty_attributes.append(attr)

        # Remove empty attributes from the object
        Builder.deleting_attributes(obj, empty_attributes)

        return obj

    @staticmethod
    def remove_none_attributes(obj):
        attributes = dict(obj.__dict__)
        none_attributes = []
        for key, value in attributes.items():
            if value is None:
                none_attributes.append(key)

            elif hasattr(value, "__dict__"):
                obj.remove_none_attributes(value)
                if not value.__dict__:
                    none_attributes.append(key)

        Builder.deleting_attributes(obj, none_attributes)

        return obj

    @staticmethod
    def remove_tagged_attributes(obj: object, tag_key: str) -> None:
        attributes = obj.__dict__
        optional_attributes = []
        for attr, value in attributes.items():
            if attr.startswith(tag_key):
                for attr_name in value:
                    optional_attributes.append(attr_name)
            elif hasattr(value, "__dict__"):
                obj.remove_tagged_attributes(value, tag_key)

        Builder.deleting_attributes(obj, optional_attributes)

        return obj

    @classmethod
    def load_from_yml(cls, filename: Path) -> None:
        """
        Loads the configuration from a YAML file.

        Args:
            filename (Path): The path to the YAML file.

        Returns:
            None
        """

        with open(filename, "r") as file:
            dic = yaml.load(file, Loader=yaml.FullLoader)

        return cls.from_dic(dic)

    def dump_to_yml(self, filename: Path, preambule="", **kwargs) -> None:
        """
        Dumps the configuration to a YAML file.

        Args:
            filename (Path): The path to the YAML file.

        Returns:
            None
        """
        # Clean attributes before dumping

        data = self.removing_attr(**kwargs)

        stream = yaml.dump(
            data,
            default_flow_style=False,
            sort_keys=False,
            indent=4,
        )

        stream = preambule + stream
        prim_attrs = [key for key in data.__dataclass_fields__]
        for attr in prim_attrs:
            stream = stream.replace(
                f"\n{attr}:\n",
                f"\n\n# {attr.capitalize()} Settings\n{attr}:\n",
            )

        create_directory(filename)

        # Actually write the file
        with open(filename, "w") as f:
            f.write(stream)

    def copy(self) -> Any:
        return copy.deepcopy(self)

    def dump_to_json(self, filename: Path, **kwargs) -> None:
        """
        Dumps the configuration to a JSON file.

        Args:
            filename (Path): The path to the JSON file.

        Returns:
            None
        """

        # Clean attributes before dumping
        data = self.removing_attr(**kwargs)

        # Intermediate yml representation
        stream = yaml.dump(
            data,
            default_flow_style=False,
            sort_keys=False,
            indent=4,
        )
        yaml_data = yaml.safe_load(stream)

        with open(filename, "w") as json_file:
            json.dump(yaml_data, json_file, indent=4)

    def removing_attr(
        self,
        rm_private=True,
        rm_optional=True,
        rm_empty=False,
        rm_none=False,
        **kwargs,
    ):
        data = self.copy()
        if rm_optional:
            data = self.remove_tagged_attributes(
                data, tag_key="_optional_attributes_"
            )
        if rm_private:
            data = self.remove_private_attributes(data)
        if rm_empty:
            data = self.remove_empty_attributes(data)
        if rm_none:
            data = self.remove_none_attributes(data)

        return data

    def add_field(self, field_name, field_value):
        setattr(self, field_name, field_value)

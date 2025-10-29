try:
    import tomllib as toml
except ImportError:
    try:
        import tomli as toml
    except ImportError:
        message = (
            "Your current python version is < 3.11, and is missing the tomli package."
            "because of this, the toml parser is unavailable."
            "please install tomli with:"
            "pip install tomli"
            "or run a python version 3.11+"
        )
        raise ImportError(message)

from abc import ABC, abstractmethod
import re

class MParser(ABC): #markup parser, yaml, toml
    def __init__(self, file_path: str):
        self.file_path = None
        try:
            self.config = self._load(file_path)
        except FileNotFoundError as e:

        self._validate()

    @abstractmethod
    def _load(self):
        self.file_path = file_path
        pass

    @abstractmethod
    def _validate(self):
        pass


class TomlParser(MParser):
    def _load(self):
        with open(self.file_path, 'rb') as fptr:
            return toml.load(fptr)

    def _validate(self):
        template = self.config.get()

    def create_submit_class(self):
        class_attrs = {}









class TomlParser(object):
    def __init__(self, toml_path: str):
        self.toml_path = toml_path
        pass

    def _load_and_parse(self):


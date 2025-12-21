from abc import ABC, abstractmethod
import re
import warnings
from batchtk.runtk.submits import SHSubmit
import sys
import os
import multiprocessing
# multiprocessing just to ensure that dynamic types are handled BEFORE spawning workers...

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


_CHECKLIST_DEFAULTS = {
    'submit_template': (
        '{output_path}',
    ),
    'script_template': (
        '{project_dir}',
        '{env}',
        '{command}',
        '{stdout}',
        '{handles}')
}

def _check(entry_key: str, entry: str, checklist: list | tuple):
    errors = []
    for check in checklist:
        if isinstance(check, str): # most common case (fastest)
            if check not in entry:
                errors.append(f"  - Missing required string: '{check}'")
        elif isinstance(check, re.Pattern): # less common case
            if check.search(entry):
                errors.append(f"  - Missing required pattern: r'{check.pattern}'")
        else: # error
            errors.append(f"  - Invalid check provided: {check} is {type(check)}. Must be str or re.Pattern.")
    if errors:
        error_details = "\n".join(errors)
        message = (
            f"Validation failed for {entry_key} with {len(errors)} error(s):\n"
            f"{error_details}\n\n"
            f"The provided entry was:\n{entry}"
            f"if you wish to override these errors, set strict=False"
        )
        # ValueError most semantically correct
        raise ValueError(message)

class Parser(ABC):
    CHECKLIST = _CHECKLIST_DEFAULTS
    def __init__(self, config: dict):
        self.config = config

    def _validate(self):
        for entry in self.config:
            checklist = self.CHECKLIST.get(entry, None)
            if isinstance(checklist, (list, tuple)):
                _check(entry, self.config[entry], checklist)
            else:
                warnings.warn(f"checklist for entry {entry} is either missing or not a valid list/tuple..."
                              f"no validation being being performed for {entry}'")



class MParser(Parser): #markup parser, yaml, toml
    def __init__(self, file_path: str, strict: bool = False):
        self.file_path = file_path
        try:
            config = self._load()
        except FileNotFoundError as e:
            raise(e)
        super().__init__(config)
        if strict:
            self._validate()

    @abstractmethod
    def _load(self):
        pass

class TomlParser(MParser):
    def _load(self):
        with open(self.file_path, 'rb') as fptr:
            return toml.load(fptr)

    def get_submit_class(self, base = SHSubmit):
        if multiprocessing.parent_process() is not None:
            raise RuntimeError(
                "Dynamic submit class creation via .toml is not supported in child processes. "
                "Please generate the submit class in the main process and pass it to child. "
                "that is, call get_submit_class() BEFORE the __main__ guard."
            )

        if not issubclass(base, SHSubmit):
            raise ValueError("must provide a base that subclasses from SHSubmit or any associated Submit")

        file_name = os.path.basename(self.file_path).replace('.', '_').replace('-', '_')
        class_name = f"CustomSubmit_{file_name}"
        
        class_attrs = {}
        for class_attr in ('submit_template', 'script_template', 'path_template', 'handles', 'key_args'):
            if class_attr in self.config:
                class_attrs[class_attr.upper()] = self.config[class_attr]

        new_class = type(
            class_name,
            (base,),
            class_attrs
        )

        new_class.__module__ = __name__
        setattr(sys.modules[__name__], class_name, new_class)
        return new_class

    def create_submit_py(self, base = SHSubmit, file_name = None, class_name = None):
        class_obj = self.get_submit_class(base=base)

        class_str = (
            f"from batchtk.runtk.submits import {base.__name__}\n",
            f"\n",
            f"class {class_name}({base.__name__}):\n",
            f"\tSUBMIT_TEMPLATE = \n"
            f"\tSCRIPT_TEMPLATE = \n"
            f"\tPATH_TEMPLATE = \n"
            f"\tHANDLES = \n"
            f"\tKEY_ARGS = \n"
        )
        return class_str

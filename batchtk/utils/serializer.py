from typing import Union
import inspect

class NamedFunc:
    def __init__(self, function, name: str=None, description: str=None, parameters: dict=None, return_opts: type | tuple | list | Union = None):
        if not callable(function):
            raise TypeError('the provided argument to NamedFunc(..., function=, ...) {} is not callable'.format(function))
        self.function = function
        self.name = name or function.__name__
        # function inspection #
        # vs.
        # from functools import cached_property @cached_property
        # performance gain from lazy loading negligible
        self.parameters = parameters
        self.return_opts = return_opts or function.__annotations__.get('return')
        if self.return_opts is not None and return_opts is None: # no argument supplied by the NamedFunc, but type hinting exists for the function itself
            self.return_opts = self.return_opts.get('__args__') # this operation supported with typing.Union hints and | operator hints
        # can do return_type checking in inherited classes, not this one... but would generate return_types
        # parameters can be populated from function.__code__.co_varnames and function.__annotations__, but not necessary to check here.
        # would rather populate that, and others, when calling __repr__ or other getinfo methods...
        self.annotations = None
        self.description = description

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def to_dict(self) -> dict:
        self.annotations = self.annotations or self.function.__annotations__
        self.parameters = self.parameters or {varname: self.annotations.get(varname, '?') for varname in self.function.__code__.co_varnames}
        self.description = self.description or self.function.__doc__ or "{}({})->{}".format(self.name, self.parameters, (self.return_opts or '?'))
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "annotations": self.annotations,
            "returns": self.return_opts,
        }

    def __repr__(self) -> str:
        return str(self.to_dict())

class SQLiteInferenceRule(NamedFunc):
    def __init__(self, function, name=None, description: str=None, parameters: dict=None, priority: int=0):
        super().__init__(function=function, name=name, description=description,
                         parameters=parameters, return_opts=('BLOB', 'INTEGER', 'REAL', 'TEXT', None, False))
        self.priority= priority # sequence for checking rules,

    def __call__(self, value):
        result = self.function(value)
        if result not in self.return_opts:
            raise RuntimeError("SQLiteInferenceRule function must return a value in: {}".format(self.return_opts))
        return result

    def __lt__(self, other):
        # allows sorting...
        if not isinstance(other, SQLiteInferenceRule):
            raise TypeError("can only compare priorities of SQLiteInferenceRules with other SQLiteInferenceRules. Instead, type:{} was provided".format(type(other)))
        return self.priority < other.priority

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }
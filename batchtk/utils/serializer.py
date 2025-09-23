from typing import Union, get_args
import inspect
from collections import namedtuple


class NamedFunc:
    def __init__(self, function, name: str=None, description: str=None, parameters: dict=None, return_opts: type | tuple | list = None):
        if not callable(function):
            raise TypeError('the provided argument to NamedFunc(..., function=, ...) {} is not callable'.format(function))
        self.function = function

        # introspection called upfront > cached_property/lazy loading
        self.name = name or function.__name__

        # get parameters and annotations
        sig = inspect.signature(function)
        self.parameters = {p.name: p.annotation if p.annotation != inspect.Parameter.empty else '?Any' for p in sig.parameters.values()}

        if return_opts:
            self.return_opts = return_opts
        else:
            return_annotation = sig.return_annotation
            if return_annotation != inspect.Signature.empty:
                args = get_args(return_annotation)
                self.return_opts = args if args else (return_annotation,)
            else:
                self.return_opts = ('?Any', )
        self.description = description or inspect.getdoc(function) or "{}({})->{}".format(self.name, self.parameters, self.return_opts)

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "returns": self.return_opts,
        }

    def __repr__(self) -> str:
        return str(self.to_dict())

class SQLiteTypeRule(NamedFunc):
    def __init__(self, function, name=None, description: str=None, parameters: dict=None, priority: int=0):
        super().__init__(function=function, name=name, description=description,
                         parameters=parameters, return_opts=('BLOB', 'INTEGER', 'REAL', 'TEXT', None, False))
        self.priority= priority # sequence for checking rules,

    def __call__(self, value):
        result = self.function(value)
        if (result.type not in self.return_opts) or (not callable(result.adapter)):
            raise RuntimeError("SQLiteInferenceRule function must return a value in: {}".format(self.return_opts))
        return result

    def __lt__(self, other):
        # allows sorting...
        if not isinstance(other, SQLiteTypeRule): # note, using NotImplemented allows the runtime to try other comparisons.
            raise NotImplemented("can only compare priorities of SQLiteInferenceRules with other SQLiteInferenceRules. Instead, type:{} was provided".format(type(other)))
        return self.priority < other.priority


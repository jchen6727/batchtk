from batchtk.header import *
from batchtk.utils import TOTPConnection, SQLiteStorage, create_logger
from fabric import Connection
from .dispatchers import *
from .runners import *
from .submits import *
from .util_class import *

from warnings import warn
class ConstructorRegistry:
    def __init__(self):
        self.SSHDispatcher = SSHDispatcher
        self.LocalDispatcher = LocalDispatcher
        self.SHSubmit = SHSubmit
        self.TOTPConnection = TOTPConnection
        self.Connection = Connection
        self.SQLiteStorage = SQLiteStorage
        self.BatchtkLogger = create_logger

    def register(self, name: str, constructor_class: type):
        if not callable(constructor_class):
            raise TypeError("The provided 'constructor_class' must be a callable class or a class constructor.")

        if hasattr(self, name):
            warn(f"Overwriting existing constructor '{name}' in this registry.")

        setattr(self, name, constructor_class())

    def __repr__(self):
        keys = [k for k in self.__dict__.keys() if not k.startswith('_')]
        return f"<ConstructorRegistry: {keys}>"

constructors = ConstructorRegistry()

del warn
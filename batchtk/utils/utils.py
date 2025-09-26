import pickle
import os
import re
import sqlite3
import subprocess
import shlex
import pandas
import itertools
from abc import abstractmethod
from typing import Protocol, runtime_checkable
import io
from batchtk.header import TABLESTR, GREPSTR, EQDELIM
from warnings import warn
from typing import Optional, Dict, List, Any
from collections import namedtuple

@runtime_checkable
class FS_Protocol(Protocol):
    """
    Protocol for all filesystem abstractions,
    any custom filesystem class must implement this protocol (runtime check)
    to be used by the dispatcher.
    """
    def exists(self, path, *args, **kwargs) -> bool:
        # check if a path maps to a resource
        pass
    def makedirs(self, path, *args, **kwargs) -> bool:
        # creates a directory path, should create intermediate directories and ignore existing directories
        # i.e. exist_ok / recreate is True
        pass
    def open(self, path, mode, *args, **kwargs) -> io.IOBase:
        # opens the file handle at path in mode where mode is 'r', 'w'
        pass
    def remove(self, path, *args, **kwargs) -> bool:
        # removes the file at path
        pass
    def close(self) -> None:
        # closes / unmounts the filesystem
        pass

class BaseFS(FS_Protocol):
    """
    Base class for filesystem abstraction
    """
    @abstractmethod
    def __init__(self):
        super().__init__()
    @abstractmethod
    def exists(self, path, *args, **kwargs):
        pass
    @abstractmethod
    def makedirs(self, path, *args, **kwargs):
        pass
    @abstractmethod
    def open(self, path, mode, *args, **kwargs):
        pass
    @abstractmethod
    def remove(self, *args, **kwargs):
        pass
    @abstractmethod
    def close(self): # PyFileSystem2 uses .close(), while fsspec uses .clear_instance_cache() and .client.close()...
        pass

    def tail(self, file, n=1):
        with self.open(file, 'r') as fptr:
            return fptr.readlines()[-n:]

    def path_open(self, path, mode): # makedirs up to a file, then open file.
        if '/' in path:
            self.makedirs(path.rsplit('/', 1)[0])
        fptr = self.open(path, mode)
        return fptr

class LocalFS(BaseFS):
    """
    Wrapper for FS protocol using os and local filesystem
    """
    def __init__(self):
        super().__init__()

    @staticmethod
    def exists(path, *args, **kwargs):
        return os.path.exists(path) # this and open() are the only two...

    @staticmethod
    def makedirs(path, *args, **kwargs):
        return os.makedirs(path, exist_ok=True)

    @staticmethod
    def open(path, *args, **kwargs):
        return open(path, *args, **kwargs)

    @staticmethod
    def remove(path, *args, **kwargs):
        return os.remove(path, *args, **kwargs)

    def close(self):
        pass

class RemoteConnFS(BaseFS): # use threading lock?
    def __init__(self, connection):
        super().__init__()
        from paramiko.ssh_exception import SSHException, BadAuthenticationType
        self.connection = connection
        self._exceptions = (SSHException, BadAuthenticationType, EOFError, OSError)
        try:
            self.connection.open()
            self.fs = connection.sftp()
        except self._exceptions as e:
            self.connection._sftp = None
            self.connection.open()
            self.fs = self.connection.sftp()


    def exists(self, path, *args, **kwargs):
        try:
            return self.connection.run('[ -e {} ]'.format(path), warn=True).return_code == 0
        except self._exceptions as e:
            self.connection.open()
            return self.connection.run('[ -e {} ]'.format(path), warn=True).return_code == 0

    def makedirs(self, path, *args, **kwargs):
        try:
            return self.connection.run('mkdir -p {}'.format(path), warn=True).return_code == 0
        except self._exceptions as e:
            self.connection.open()
            return self.connection.run('mkdir -p {}'.format(path), warn=True).return_code == 0

    def open(self, path, mode, *args, **kwargs):
        if self.fs is None:
            try:
                self.connection.open()
                self.fs = self.connection.sftp()
            except self._exceptions as e:
                self.connection.open()
                self.fs = self.connection.sftp()
        try:
            return self.fs.file(path, mode)
        except self._exceptions as e:
            self.connection._sftp = None
            self.connection.open()
            self.fs = self.connection.sftp()
            return self.fs.file(path, mode)
        except Exception as e:
            raise e

    def remove(self, path, *args, **kwargs):
        try:
            return self.connection.run('rm {}'.format(path), warn=True).return_code == 0
        except self._exceptions as e:
            self.connection.open()
            return self.connection.run('rm {}'.format(path), warn=True).return_code == 0
    def close(self):
        self.fs.close()
        self.fs = None
        self.connection._sftp = None
        #self.connection.close() # keep self.connection open.

class CustomFS(BaseFS):
    def __new__(cls, fs: FS_Protocol):
        if isinstance(fs, BaseFS): # returns the same object if it is properly subclassed
            return fs
        if not isinstance(fs, FS_Protocol):
            raise TypeError("fs does not fully implement FS_Protocol (see batchtk/utils/utils")
        return super().__new__(cls)

    def __init__(self, fs: FS_Protocol):
        if isinstance(fs, BaseFS):
            return
        self.fs = fs

    def exists(self, path, *args, **kwargs):
        return self.fs.exists(path, *args, **kwargs)

    def makedirs(self, path, *args, **kwargs):
        return self.fs.makedirs(path, *args, **kwargs)

    def open(self, path, mode, *args, **kwargs):
        return self.fs.open(path, mode, *args, **kwargs)

    def remove(self, path, *args, **kwargs):
        return self.fs.remove(path, *args, **kwargs)

    def close(self):
        return self.fs.close()

@runtime_checkable
class Cmd_Protocol(Protocol):
    proc: object
    def run(self, command: str) -> object:
        pass
    def close(self) -> None:
        pass

class BaseCmd(Cmd_Protocol):
    def __init__(self):
        self.proc = None
    @abstractmethod
    def run(self, command):
        pass
    def close(self):
        self.proc = None

class LocalProcCmd(BaseCmd):
    def __init__(self):
        super().__init__()
        self.proc = None

    def run(self, command):
        self.proc = subprocess.run(command.split(' '), text=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        return self.proc

class RemoteConnCmd(BaseCmd):
    def __init__(self, connection):
        from paramiko.ssh_exception import SSHException, BadAuthenticationType
        super().__init__()
        self.connection = connection
        self.proc = None
        self._exceptions = (SSHException, BadAuthenticationType, EOFError, OSError)

    def run(self, command):
        try:
            self.proc = self.connection.run(command, warn=True, hide=True)
            return self.proc
        except self._exceptions as e:
            self.connection.open()
            self.proc = self.connection.run(command, warn=True, hide=True)
            return self.proc

class CustomCmd(BaseCmd):
    def __new__(cls, cmd: Cmd_Protocol):
        if isinstance(cmd, BaseCmd):
            return cmd
        if not isinstance(cmd, Cmd_Protocol):
            raise TypeError("cmd does not fully implement Cmd_Protocol (see batchtk/utils/utils")
        return super().__new__(cls)
    def __init__(self, cmd: Cmd_Protocol):
        if isinstance(cmd, BaseCmd):
            return
        super().__init__()
        self.cmd = cmd
        self.proc = None

    def run(self, command):
        self.proc = self.cmd.run(command)
        return self.cmd.run(command)

class TOTPConnection(object):
    def __init__(self, host, key):
        import pyotp
        from fabric import Connection
        self.totp = pyotp.TOTP(key)
        self.connection = Connection(host=host, connect_kwargs={'password': self.totp.now()})

    def sftp(self):
        return self.connection.sftp()

    def open(self):# multithreading checks for TOTP
        from paramiko.ssh_exception import BadAuthenticationType
        orig = self.totp.now()
        while True:
            while orig == self.totp.now(): #await new totp
                pass
            try:
                self.connection.connect_kwargs['password'] = self.totp.now()
                self.connection.open()
                return
            except BadAuthenticationType as e:
                continue

    def run(self, command, warn=False, hide=True):
        return self.connection.run(command, warn=warn, hide=hide)

    @property
    def _sftp(self):
        return self.connection._sftp

    @_sftp.setter
    def _sftp(self, value):
        self.connection._sftp = value

class FutureValue:
    def __init__(self, name: Optional[str] = None):
        self._value = None
        self._resolved = False
        self.name = name

    def set(self, value: Any):
        """Set the value and mark it as resolved."""
        self._value = value
        self._resolved = True

    def get(self) -> Any:
        """Retrieve the value if resolved, otherwise raise an error."""
        if not self._resolved:
            raise ValueError(f"FutureValue '{self.name}' has not been resolved yet.")
        return self._value

    def is_resolved(self) -> bool:
        """Check if the value has been resolved."""
        return self._resolved

def format_env(dictionary: dict, value_type= None, index = 0, grepstr = GREPSTR, eqdelim = EQDELIM):
    # function is round-tripping safe (float/numpy->str->float/numpy) for > python 3.1
    get_type = staticmethod(lambda x: type(x).__name__)
    return {"{}{}{}".format(value_type or get_type(value).upper(), grepstr, index + i):
                "{}{}{}".format(key, eqdelim, value) for i, (key, value) in enumerate(dictionary.items())}


def get_path(path):
    path_opt = {
        '~': os.path.expanduser,
        '.': os.path.abspath,
        '/': os.path.abspath,
    }
    try:
        return path_opt[path[0]](path)
    except KeyError:
        raise ValueError("supplied path must start with an absolute (/), relative (.), or user home (~)")

def write_pkl(wobject: object, write_path: str):
    if '/' in write_path:
        os.makedirs(write_path.rsplit('/', 1)[0], exist_ok=True)
    with open(write_path, 'wb') as fptr:
        pickle.dump(wobject, fptr)


def read_pkl(read_path: str):
    with open(read_path, 'rb') as fptr:
        robject = pickle.load(fptr)
    return robject


def local_open(path: str, mode: str): # renamed, avoid confusion with the fs.path_open
    if '/' in path:
        os.makedirs(path.rsplit('/', 1)[0], exist_ok=True)
    fptr = open(path, mode)
    return fptr

def validate_path(path: str):
    return #now using updated EQDELIM --

def create_path(path0: str, path1 = "", fs = LocalFS()):
    if path1 and path1[0] == '/':
        target = os.path.normpath(path1)
    else:
        target = os.path.normpath(os.path.join(path0, path1))
    validate_path(target)
    if fs is None:
        return target
    if isinstance(fs, FS_Protocol):
        try:
            fs.makedirs(target)
            return target
        except Exception as e:
            raise Exception("attempted to create from ({},{}) path: {} and failed with exception: {}".format(path0, path1, target, e))
    else:
        raise TypeError("user provided a fs that does not implement FS_Protocol")


def get_exports(filename=None, script=None):
    if filename and script:
        warn("both filename and script provided, using script")
    if script:
        items = re.findall(r'export (.*?)="(.*?)"', script)
        return {key: val for key, val in items}
    if filename:
        with open(filename, 'r') as fptr:
            items = re.findall(r'export (.*?)="(.*?)"', fptr.read())
            return {key: val for key, val in items}
    raise ValueError("either filename or script must be provided")

def get_port_info(port):
    output = subprocess.run(shlex.split('lsof -i :{}'.format(port)), capture_output=True, text=True)
    if output.returncode == 0:
        return output.stdout
    else:
        return output.returncode


""" # old Storage class # deprecating, now see storage.py

class Storage(object):# Use as TrialTable or Table object nomenclature to avoid confusion with logger
    def __init__(self):
        self.path = None

    def init_db(self): # initializes the database
        pass

    def get_schema(self): # get the schema of the storage
        pass

    def add_columns(self, schema: dict): # add new columns to storage
        pass

    def insert(self, entry: dict):#replace log with "insert" // see below
        pass

    def close(self):
        pass

class SQLiteStorage(Storage): #SQLiteTable...
    def __init__(self,
                 label: str ='trials',
                 path: str = '.',
                 entries: Optional[Dict|List] = None,
                 add_trial_metadata: bool = True):
        from filelock import FileLock
        import sqlite3
        super().__init__()
        path = get_path(path)
        os.makedirs(path, exist_ok=True)
        self.label = label
        if entries is None:
            self.entries = dict()
        elif isinstance(entries, (list, tuple)) and all(isinstance(entry, str) for entry in entries):
            self.entries = {entry: 'TEXT' for entry in entries}
        else:
            self.entries = entries
        assert isinstance(self.entries, dict)
        if add_trial_metadata:
            self.entries = {'trial_path': 'TEXT', 'trial_label': 'TEXT'} | self.entries # can do TEXT NOT NULL or TEXT DEFAULT None for missing insertions...
        self.path = "{}/{}.sqlite.db".format(path, label)
        self._connect = sqlite3.connect
        self._lock = FileLock("{}.lock".format(self.path))
        self._oe = sqlite3.OperationalError
        self.init_db()

    def get_schema(self):
        with self._lock:
            conn = self._connect(self.path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info({})".format(self.label))
            data = cursor.fetchall()
            conn.close()
        schema = {column[1]: column[2] for column in data} # not set operation,
        return schema

    def init_db(self):
        if os.path.exists(self.path): # check that the db is appropriate if it exists ---
            schema = self.get_schema() # after init, check schema only once, then treat entries.keys as the relevant metadata
            if set(self.entries.items()) <= set(schema.items()):
                self.entries = schema # update entries to the current schema, if it is a subset of the expected entries
                return
            else:
                raise ValueError(f"database at path {self.path} expects different entries than given: schema {schema} conflicts with entries {self.entries}")
        exec_str = "id INTEGER PRIMARY KEY AUTOINCREMENT, {}".format(','.join(["[{}] {}".format(k, v) for k, v in self.entries.items()]))
        exec_str = "CREATE TABLE IF NOT EXISTS {} ({})".format(self.label, exec_str)
        with self._lock:
            conn = self._connect(self.path)
            cursor = conn.cursor()
            cursor.execute(exec_str)
            conn.commit()
            conn.close()

    def insert(self, entries: dict): # record/add/insert/save
        if not set(entries.keys()) <= set(self.entries.keys()):
            raise ValueError(f"entries keys exceed expected keys: {entries.keys()} != {self.entries.keys()}")
        keys, vals = zip(*entries.items())
        exec_str = "INSERT INTO {} ([{}]) VALUES ({})".format(self.label, '],['.join(keys), ','.join(['?'] * len(vals)))
        with self._lock:
            conn = self._connect(self.path)
            cursor = conn.cursor()
            cursor.execute(exec_str, vals)
            conn.commit()
            conn.close()

    def add_columns(self, columns: list | tuple | dict) -> list[tuple[str, Exception]]:
        #clarify nomenclature, header implies creation of metadata for a DB
        # compare columns against existing self.entries ---
        if isinstance(columns, (list, tuple)):
            new_columns = {column: 'TEXT' for column in columns if column not in self.entries.keys()}
        if isinstance(columns, dict):
            new_columns = {key: value for key, value in columns.items() if key not in self.entries.keys()}
        exec_strs = ["ALTER TABLE {} ADD COLUMN [{}] {}".format(self.label, new_column, new_value)
                     for new_column, new_value in new_columns.items()]
        oe = []
        with self._lock:
            conn = self._connect(self.path)
            cursor = conn.cursor()
            for new_column, exec_str in zip(new_columns.keys(), exec_strs):
                try:
                    cursor.execute(exec_str)
                    oe.append( (new_column, None) )
                except self._oe as e:
                    oe.append( (new_column, e) )
            conn.commit()
            conn.close()
        self.entries = self.get_schema()
        return oe


    def to_df(self):
        exec_str = "SELECT * FROM {}".format(self.label)
        with self._lock:
            conn = self._connect(self.path)
            cursor = conn.cursor()
            cursor.execute(exec_str)
            rows = cursor.fetchall()
            description = cursor.description
            conn.close()
        columns = [column[0] for column in description]
        df = pandas.DataFrame(rows, columns=columns)
        return df

    def find(self, column: str, value: Any):
        if column not in self.entries:
            raise ValueError(f"column {column} not in entries: {self.entries}")
        exec_str = "SELECT * FROM {} WHERE {} = ?".format(self.label, column)
        with self._lock:
            conn = self._connect(self.path)
            cursor = conn.cursor()
            cursor.execute(exec_str, [value])
            rows = cursor.fetchall()
            description = cursor.description
            conn.close()
        if not rows:
            return None
        columns = [column[0] for column in description]
        df = pandas.DataFrame(rows, columns=columns)
        return df

    def close(self):
        os.remove(self._lock.lock_file)
        self._lock = None


"""


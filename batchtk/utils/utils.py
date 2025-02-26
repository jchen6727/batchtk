import pickle
import os
import re
import subprocess
import shlex
import pandas
import itertools
from abc import abstractmethod
from typing import Protocol, runtime_checkable
import io
from batchtk.header import GREPSTR, EQDELIM
from warnings import warn
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

class RemoteSSHFS(BaseFS):
    def __init__(self, host = None):
        super().__init__()
        import sshfs
        self.fs = sshfs.SSHFileSystem(host)
        self.fs.cachable = False

    def exists(self, path, *args, **kwargs):
        return self.fs.exists(path, *args, **kwargs)

    def makedirs(self, path, *args, **kwargs):
        return self.fs.makedirs( path, exist_ok=True, *args, **kwargs)

    def open(self, path, mode, *args, **kwargs):
        return self.fs.open(path, mode, *args, **kwargs) #the user has to remember to either call w/ context manager or close...

    def remove(self, path, *args, **kwargs):
        return self.fs.rm(path, *args, **kwargs)

    def close(self):
        self.fs.client.close()
        self.fs.clear_instance_cache()

class RemoteConnFS(BaseFS): # use threading lock?
    def __init__(self, connection):
        super().__init__()
        from paramiko.ssh_exception import SSHException
        self.connection = connection
        self.connection.open()
        self.fs = connection.sftp()
        self._exception = SSHException



    def exists(self, path, *args, **kwargs):
        try:
            return self.connection.run('[ -e {} ]'.format(path), warn=True).return_code == 0
        except (EOFError, self._exception, OSError) as e:
            self.connection.open()
            return self.connection.run('[ -e {} ]'.format(path), warn=True).return_code == 0

    def makedirs(self, path, *args, **kwargs):
        try:
            return self.connection.run('mkdir -p {}'.format(path), warn=True).return_code == 0
        except (EOFError, self._exception, OSError) as e:
            self.connection.open()
            return self.connection.run('mkdir -p {}'.format(path), warn=True).return_code == 0

    def open(self, path, mode, *args, **kwargs):
        if self.fs is None:
            self.connection.open()
            self.fs = self.connection.sftp()
        try:
            return self.fs.file(path, mode)
        except (EOFError, self._exception, OSError) as e:
            self.connection._sftp = None
            self.connection.open()
            self.fs = self.connection.sftp()
            return self.fs.file(path, mode)
        except Exception as e:
            raise e

    def remove(self, path, *args, **kwargs):
        try:
            return self.connection.run('rm {}'.format(path), warn=True).return_code == 0
        except (EOFError, self._exception, OSError) as e:
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
        from paramiko.ssh_exception import SSHException
        super().__init__()
        self.connection = connection
        self.proc = None
        self._exception = SSHException

    def run(self, command):
        try:
            self.proc = self.connection.run(command, warn=True, hide=True)
            return self.proc
        except (EOFError, self._exception, OSError) as e:
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

def format_env(dictionary: dict, value_type= None, index = 0, grepstr = GREPSTR, eqdelim = EQDELIM):
    get_type = staticmethod(lambda x: type(x).__name__)
    return {"{}{}{}".format(value_type or get_type(value).upper(), grepstr, index + i):
                "{}{}{}".format(key, eqdelim, value) for i, (key, value) in enumerate(dictionary.items())}


def get_path(path):
    if path[0] == '/':
        return os.path.normpath(path)
    elif path[0] == '.':
        return os.path.normpath(os.path.join(os.getcwd(), path))
    else:
        raise ValueError("path must be an absolute path (starts with /) or relative to the current working directory (starts with .)")

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

def batchify( batch_dict, bin_size = 1, file_label = None ):
    """
    batch_dict = {string: list}
    bin_size = integer
    file_label = string
    --------------------------------------------------------------------------------------------------------------------
    creates a list of pandas dataframes, if file_label exists, each pandas dataframe is written to a csv file.
    """
# rewrite using pandas.cut ? : https://pandas.pydata.org/docs/reference/api/pandas.cut.html
    bins = []

    bin_num = 0
    curr_size = 0
    curr_batch = []

    for run, batch in enumerate(dcx(**batch_dict)):
        batch.update({"run": run})
        curr_batch.append(pandas.Series(batch))
        curr_size += 1
        if curr_size == bin_size:
            curr_size = 0
            bin_df = pandas.DataFrame(curr_batch)
            curr_batch = []
            bins.append(bin_df)
            # write bin to csv if file_label
            if file_label:
                filename = "{}{}.csv".format(file_label, bin_num)
                bin_num += 1
                bin_df.to_csv(filename, index=False)
    if curr_batch:
        # write last batch if empty
        bin_df = pandas.DataFrame(curr_batch)
        bins.append(bin_df)
        if file_label:
            filename = "{}{}.csv".format(file_label, bin_num)
            bin_df.to_csv(filename, index=False)
    return bins

def dcx(**kwargs):
    """
    Dictionary preserving Cartesian (x) product, returned as a generator
    https://stackoverflow.com/questions/5228158/cartesian-product-of-a-dictionary-of-lists
    """
    for instance in itertools.product(*kwargs.values()):
        yield dict(zip(kwargs.keys(), instance))

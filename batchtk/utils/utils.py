import pickle
import os
import re
import subprocess
import shlex
import pandas
import itertools
import fsspec
import sshfs
from abc import abstractmethod


class BaseFS(fsspec.AbstractFileSystem):
    """
    Base class for fsspec filesystem abstraction
    """
    @abstractmethod
    def __init__(self):
        super().__init__()
    @abstractmethod
    def exists(self, *args, **kwargs):
        pass
    @abstractmethod
    def makedirs(self, *args, **kwargs):
        pass
    @abstractmethod
    def open(self, *args, **kwargs):
        pass
    @abstractmethod
    def remove(self, *args, **kwargs):
        pass
    @abstractmethod
    def close(self):
        pass

    def tail(self, file, n=1):
        with self.open(file, 'r') as fptr:
            return fptr.readlines()[-n:]

    def path_open(self, path, mode):
        if '/' in path:
            self.makedirs(path.rsplit('/', 1)[0], exist_ok=True)
        fptr = self.open(path, mode)
        return fptr

class LocalFS(BaseFS):
    """
    Wrapper for fsspec filesystem abstraction
    """
    def __init__(self):
        super().__init__()

    @staticmethod
    def exists(*args, **kwargs):
        return os.path.exists(*args, **kwargs) # this and open() are the only two...

    @staticmethod
    def makedirs(*args, **kwargs):
        return os.makedirs(*args, **kwargs)

    @staticmethod
    def open(*args, **kwargs):
        return open(*args, **kwargs)

    @staticmethod
    def remove(*args, **kwargs):
        return os.remove(*args, **kwargs)

    def close(self):
        pass

class RemoteFS(BaseFS):
    def __init__(self, fs = None, host = None):
        super().__init__()
        self.fs = None
        if fs and isinstance(fs, fsspec.AbstractFileSystem):
            self.fs = fs
        if self.fs is None and host:
            self.fs = sshfs.SSHFileSystem(host)
        if not self.fs:
            raise ValueError("no fsspec valid filesystem or host provided")

    def exists(self, *args, **kwargs):
        return self.fs.exists(*args, **kwargs)

    def makedirs(self, *args, **kwargs):
        return self.fs.makedirs(*args, **kwargs)

    def open(self, *args, **kwargs):
        return self.fs.open(*args, **kwargs) #the user has to remember to either call w/ context manager or close...

    def remove(self, *args, **kwargs):
        return self.fs.rm(*args, **kwargs)

    def close(self):
        self.fs.clear_instance_cache()

class BaseCmd(object):
    @abstractmethod
    def __init__(self):
        self.proc = None
    @abstractmethod
    def run(self, command):
        pass

class LocalCmd(BaseCmd):
    def __init__(self):
        super().__init__()
        self.proc = None

    def run(self, command):
        self.proc = subprocess.run(command.split(' '), text=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        return self.proc

class RemoteCmd(BaseCmd):
    def __init__(self, connection):
        super().__init__()
        self.connection = connection
        self.proc = None

    def run(self, command):
        self.proc = self.connection.run(command, warn=True, hide=True)
        return self.proc

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


def path_open(path: str, mode: str):#TODO eventually get rid of this function (see classes)
    if '/' in path:
        os.makedirs(path.rsplit('/', 1)[0], exist_ok=True)
    fptr = open(path, mode)
    return fptr

def validate_path(path: str):
    if '=' in path:
        raise ValueError("error: the directory path created for your search results contains the special character =")

def create_path(path0: str, path1 = "", fs = os):
    if path1 and path1[0] == '/':
        target = os.path.normpath(path1)
    else:
        target = os.path.normpath(os.path.join(path0, path1))
    validate_path(target)
    if fs is None:
        return target
    if hasattr(fs, 'makedirs'):
        try:
            fs.makedirs(target, exist_ok=True)
            return target
        except Exception as e:
            raise Exception("attempted to create from ({},{}) path: {} and failed with exception: {}".format(path0, path1, target, e))
    else:
        raise ValueError("user provided a fs without a makedirs method, please provide a valid implementation of fsspec")


def get_exports(filename):
    with open(filename, 'r') as fptr:
        items = re.findall(r'export (.*?)="(.*?)"', fptr.read())
        return {key: val for key, val in items}

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


def format_val(val):
    """
    Nested objects with numpy or other data types?
    Parameters
    ----------
    val

    Returns
    -------
    """
    return None
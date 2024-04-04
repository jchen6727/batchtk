import pickle
import os
import re
import subprocess
import shlex
import pandas
import itertools

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


def path_open(path: str, mode: str):
    if '/' in path:
        os.makedirs(path.rsplit('/', 1)[0], exist_ok=True)
    fptr = open(path, mode)
    return fptr

def create_path(path0: str, path1 = ""):
    if path1 and path1[0] == '/':
        target = os.path.normpath(path1)
    else:
        target = os.path.normpath(os.path.join(path0, path1))
    try:
        os.makedirs(target, exist_ok=True)
        return target
    except Exception as e:
        raise Exception("attempted to create from ({},{}) path: {} and failed with exception: {}".format(path0, path1, target, e))

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

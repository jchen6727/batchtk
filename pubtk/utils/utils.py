import pickle
import os
import re
import subprocess
import shlex

def write_pkl(wobject: object, write_path: str):
    if '/' in write_path:
        os.makedirs(write_path.rsplit('/', 1)[0], exist_ok=True)
    with open(write_path, 'wb') as fptr:
        pickle.dump(wobject, fptr)


def read_pkl(read_path: str):
    fptr = open(read_path, 'rb')
    robject = pickle.load(fptr)
    return robject


def path_open(path: str, mode: str):
    if '/' in path:
        os.makedirs(path.rsplit('/', 1)[0], exist_ok=True)
    fptr = open(path, mode)
    return fptr


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
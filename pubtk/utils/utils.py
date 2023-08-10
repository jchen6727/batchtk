import pickle
import os
def write_pkl(wobject: object, write_path: str):
    if '/' in write_path:
        os.makedirs(write_path.rsplit('/', 1)[0], exist_ok=True)
    fptr = open(write_path, 'wb')
    pickle.dump(wobject, fptr)
    fptr.close()

def read_pkl(read_path: str):
    fptr = open(read_path, 'rb')
    robject = pickle.load(fptr)
    return robject


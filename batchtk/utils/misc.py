import os
from batchtk.utils import BaseCmd

#TODO add some more generalizable string and path checking....
def _get_obj_args(self, __class__, **kwargs): # note that _ does not get captured by "import *"
    kwargs.update(kwargs.pop('kwargs'))
    return kwargs



def expand_local_path(path, create_dirs=True):
    """
    expand a path on the local filesystem.
    Parameters
    ----------
    path : str  path with characters ('~', '.', '/') to resolve
    create_dirs : bool True create any directories in the path that do not exist
                            any ending files (by extensions) will be ignored

    """
    path_opt = {
        '~': os.path.expanduser,
        '.': os.path.abspath,
        '/': os.path.abspath,
    }
    if not (path.startswith( ('/', '~/', './', '../') ) or path in ('~', '.', '..')):
        raise ValueError("supplied path must either start with an absolute (/), \n\
                          relative (./, ../), user home (~), or be exactly one of: \n\
                          (~ , ., ..)\n\
                          got: {}".format(path))
    return_path = path_opt[path[0]](path)
    if return_path in ('/',):
        raise ValueError("supplied path resolves to root (/), which is not allowed")
    if create_dirs:
        if os.path.splitext(return_path)[1] == '':
            os.makedirs(return_path, exist_ok=True)
        else:
            os.makedirs(os.path.dirname(return_path), exist_ok=True)
    return return_path

expand_path = expand_local_path # alias this for now ...
def expand_remote_path(path, create_dirs=False, remote_connection=None): # unstable fix
    if not isinstance(remote_connection, BaseCmd):
        raise ValueError('remote_connection must be an instance of BaseCmd, however, type({}) was provided'.format(type(remote_connection)))
    return_path = remote_connection.run('readlink -f -n {}'.format(path)).stdout
    if create_dirs:
        if os.path.splitext(return_path)[1] == '':
            remote_connection.run('mkdir -p {}'.format(return_path))
        else:
            remote_connection.run("mkdir -p \"$(dirname '{}')\"".format(return_path))
    return return_path

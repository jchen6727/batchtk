import os

def _get_obj_args(self, __class__, **kwargs): # note that _ does not get captured by "import *"
    kwargs.update(kwargs.pop('kwargs'))
    return kwargs

def expand_path(path, create_dirs=False):
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
        os.makedirs(return_path, exist_ok=True)
    return return_path
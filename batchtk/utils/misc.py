import os

def _get_obj_args(self, __class__, **kwargs): # note that _ does not get captured by "import *"
    kwargs.update(kwargs.pop('kwargs'))
    return kwargs

def expand_path(path, create=True):
    path_opt = {
        '~': os.path.expanduser,
        '.': os.path.abspath,
        '/': os.path.abspath,
    }
    if not (path.startswith( ('~/', './', '../') ) or path in ('~', '.', '..')):
        raise ValueError("supplied path must either start with an absolute (/), relative (./, ../), user home (~), or be exactly one of: (~ , ., ..)")
    return path_opt[path[0]](path)
from batchtk.runtk.runners import get_runner
import collections

def traverse(obj, path):
    if len(path) == 1: #access object in dictionary
        assert path[0] in obj
        return obj
    if isinstance(obj, collections.abc.Mapping) and path[0] in obj: #access object in dictionary
        return traverse(obj[path[0]], path[1:])
    if isinstance(obj, collections.abc.Mapping) and eval(path[0]) in obj: #access object in dictionary
        return traverse(obj[int(path[0])], path[1:])
    if isinstance(obj, collections.abc.Sequence) and path[0].isdigit(): #access integer in list
        return traverse(obj[int(path[0])], path[1:])
    else:
        raise AssertionError("error accessing {}[{}]".format(obj, path[0]))

def set_map(obj, assign_path, value):
    if isinstance(assign_path, str) and '.' in assign_path:
        assigns = assign_path.split('.')
    else:
        assigns = assign_path # assume list
    try:
        traverse(obj, assigns)[assigns[-1]] = value
    except AssertionError:
        raise ValueError("error setting {}={}, check that path {} exists within your object mapping".format(assign_path, value, assign_path))

def create_map(obj, assign_path, value):
    if isinstance(assign_path, str) and '.' in assign_path:
        assigns = assign_path.split('.')
    else:
        assigns = assign_path # assume list
    for assign in assigns[:-1]:
        if assign not in obj:
            obj[assign] = {}
        obj = obj[assign]
    obj[assigns[-1]] = value

def update_config(obj, *args, **kwargs):
    for arg in args:
        if len(arg) == 2:
            set_map(obj, arg[0], arg[1])
        else:
            set_map(obj, arg[:-1], arg[-1])
    for key, value in kwargs.items():
        set_map(obj, key, value)


def create_config(obj, *args, **kwargs):
    for arg in args:
        if len(arg) == 2:
            create_map(obj, arg[0], arg[1])
        else:
            create_map(obj, arg[:-1], arg[-1])



class RunConfig(dict):
    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], dict):
            super().__init__(args[0], **kwargs)
            args = args[1:]
        else:
            super().__init__(**kwargs)
        self._runner = get_runner()
        self._mappings = self._runner.get_mappings()
        create_config(self, *args)

    def update(self, *args, **kwargs):
        update_config(self, *args, **kwargs)

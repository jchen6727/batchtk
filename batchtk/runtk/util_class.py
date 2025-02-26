from batchtk.runtk.runners import Runner, get_runner
import ast
import collections

def traverse(obj, path):
    if len(path) == 1: #access object in dictionary
        assert path[0] in obj or ast.literal_eval(path[0]) in obj or int(path[0]) < len(obj), "error accessing {}[{}]".format(obj, path[0])
        return obj
    if isinstance(obj, collections.abc.Mapping) and path[0] in obj: #access object in dictionary
        return traverse(obj[path[0]], path[1:])
    if isinstance(obj, collections.abc.Mapping) and ast.literal_eval(path[0]) in obj: #access object in dictionary
        return traverse(obj[int(path[0])], path[1:])
    if isinstance(obj, collections.abc.Sequence) and path[0].isdigit() and int(path[0]) < len(obj): #access int in list
        return traverse(obj[int(path[0])], path[1:])
    else:
        raise AssertionError("error accessing {}[{}]".format(obj, path[0]))

def set_map(obj, assign_path, value):
    if isinstance(assign_path, str): # 'string'.split('.') -> ['string'], 'string.split'.split('.') -> ['string', 'split]
        assigns = assign_path.split('.')
    else:
        assigns = assign_path # assume list
    try:
        container = traverse(obj, assigns)
    except AssertionError:
        raise ValueError("error setting {}={}, check that path {} exists within your object mapping".format(assign_path, value, assign_path))
    try:
        container[assigns[-1]] = value
    except TypeError:
        container[ast.literal_eval(assigns[-1])] = value


def create_map(obj, assign_path, value):
    if isinstance(assign_path, str):
        assigns = assign_path.split('.')
    else:
        assigns = assign_path # assume list or string
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
            self._runner = get_runner()
        else:
            super().__init__(**kwargs)
        self._runner = 'runner' in kwargs and kwargs['runner'] or get_runner()
        self._mappings = self._runner.get_mappings()
        create_config(self, *args)

    def update(self, *args, **kwargs):
        kwargs = kwargs | self._mappings
        update_config(self, *args, **kwargs)

    def __getattr__(self, k):
        try:
            # Throws exception if not in prototype chain
            return object.__getattribute__(self, k)
        except AttributeError:
            try:
                return self[k]
            except KeyError:
                raise AttributeError(k)

    def __setattr__(self, k, v):
        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                self[k] = v
            except:
                raise AttributeError(k)
        else:
            object.__setattr__(self, k, v)

    def __delattr__(self, k):
        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                del self[k]
            except KeyError:
                raise AttributeError(k)
        else:
            object.__delattr__(self, k)

    @property
    def __dict__(self):
        return {key: value for key, value in self.items() if not key.startswith('_')}

class Comm(object):
    def __init__(self, runner=None):
        self._runner = runner or get_runner()

    def connect(self):
        self._runner.connect()

    def send(self, data):
        self._runner.send(data)

    def receive(self):
        return self._runner.receive()

    def close(self):
        self._runner.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.close()

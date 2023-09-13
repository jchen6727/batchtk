def convert(self: object, _type: str, val: object):
    if _type in self._supports:
        return self._supports[_type](val)
    if _type == '':
        for _type in self._supports:
            try:
                return self._supports[_type](val)
            except:
                pass
    raise KeyError(_type)

def set_map(self, assign_path, value):
    assigns = assign_path.split('.')
    crawler = self.__getitem__(assigns[0])
    for gi in assigns[1:-1]:
        crawler = crawler.__getitem__(gi)
    crawler.__setitem__(assigns[-1], value)

def create_script(env, filename, template, **kwargs):
    """
    # make_script
    # env: dictionary of environment variables to copy to script
    # template: script template
    # filename: filename of script
    # template: template of script to be formatted
    """
    fptr = open(filename, 'w')
    # create an environment string to be inserted into script
    # environment string will be handled via export commands, e.g.:
    # export VAR0="VAL0"
    envstr = '\nexport ' + '\nexport '.join(['{}="{}"'.format(key, val) for key, val in env.items()])
    shstr = template.format(env=envstr, **kwargs)
    fptr.write(shstr)
    fptr.close()

def handle_inputs(kwargs, aliases_list):
    """
    # handle alias in kwargs dictionary, i.e. if there is an "id" entry but not a "name" entry" will create a "name" entry with the same value as "id"
    # kwargs: input arguments
    # aliases_list: iterable of iterables, each group of iterables is a sequence entries that are aliased to each other: e.g.
        ( ("id", "name"), ("cwd", "path", "jobPath") )
        will alias "id" <-> "name"
        will alias "cwd" <-> "path" <-> "jobPath"
    # in clashes, priority goes to last element of the iterable.
    """
    for aliases in aliases_list:
        item = None
        for alias in aliases:
            if alias in kwargs:
                item = kwargs[alias]
        if item:
            for alias in aliases:
                kwargs[alias] = item
    return kwargs
        

class Group(object):
    obj_list = [] # each dispatcher object added to this list
    count = 0 # persistent count
    def __init__(self, obj):
        self.obj = obj

    def new(self, **kwargs):
        kwargs['id'] = self.count
        _obj = self.obj( **kwargs )
        self.obj_list.append(_obj)
        self.count = self.count + 1
        return _obj

    def __getitem__(self, i):
        return self.obj_list[i]


class Alias(object):


#https://realpython.com/lessons/decoding-custom-types-json/

class AttrObject(object):
    """
    # object that can be accessed via attributes
    # e.g.:
    # obj = AttrObject()
    # obj.a = 1
    # obj.b = 2
    # obj.c = 3
    # obj['a'] = 1
    # obj['b'] = 2
    # obj['c'] = 3
    # obj['a'] == obj.a
    # obj['b'] == obj.b
    # obj['c'] == obj.c
    """
    def __init__(self, aliases = None, **kwargs):
        if aliases:
            self.aliases = aliases
        else:
            self.aliases = {}
        self.__dict__.update(kwargs)
        self.__name__ = 'AttrObject'
        self.__origin__ = 'AttrObject'

    def __getitem__(self, k):
        return self.__dict__[k]

    def __setitem__(self, k, v):
        self.__dict__[k] = v

    def __setattr__(self, k, v):
        self.__dict__[k] = v

    def __getattr__(self, k): # __getattr__ only called when __getattribute__ fails
        # implied that __getattribute__ is called first
        if k in self.__dict__:
            return self.__dict__[k]
        elif k in self.aliases:
            return self.__dict__[self.aliases[k]]
        else:
            raise KeyError(k)

    def __repr__(self):
        aliases = self.__dict__.pop('aliases', None)
        rstr = """\
aliases:
{}
========================================
attributes:
{}
""".format(aliases, self.__dict__)
        self.__dict__['aliases'] = aliases
        return rstr

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
    if len(assigns) == 1:
        self.__setitem__(assigns[0], value)
        return
    crawler = self.__getitem__(assigns[0])
    for gi in assigns[1:-1]:
        crawler = crawler.__getitem__(gi)
    crawler.__setitem__(assigns[-1], value)
    return

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

class Aliases(object):
    def __init__(self, aliases, **kwargs):
        self.aliases = aliases
        self.aliases.update(kwargs)
    def __getattr__(self, k):
        if k in self.env:
            return self.env[k]
        elif k in self.aliases:
            return self.env[self.aliases[k]]
        else:
            raise KeyError(k)

    def __getitem__(self, k):
        try:
            return object.__getattribute__(self, k)
        except:
            raise KeyError(k)


def gs_item(self: object, item: str, val: object):
    #try __getitem__, if fails, use __setitem__
    try:
        return self.__getitem__(val)
    except:
        self.__setitem__(val, dict())
        return self.__getitem__(val)


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

def set_map_f(self, assign_path, value, force=False):
    assigns = assign_path.split('.')
    crawler = gs_item(self, assigns[0])
    for gi in assigns[1:-1]:
        crawler = gs_item(self, gi)
    pass

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


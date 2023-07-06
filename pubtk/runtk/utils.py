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

def make_script(env, script, file, **kwargs):
    """
    # make_script
    # env: environment variables
    # script: script to run
    """

    return '\n'.join(['{}={}'.format(key, val) for key, val in env.items()] + [script])
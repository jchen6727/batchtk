def _get_obj_args(self, __class__, **kwargs): # note that _ does not get captured by "import *"
    kwargs.update(kwargs.pop('kwargs'))
    return kwargs


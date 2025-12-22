import warnings
from batchtk import header

def deprecated_arg(kwarg_map: dict, deprecated_since: str=None, removal_when: str=None):
    def decorator(func):
        def wrapped(*args, **kwargs):
            new_kwargs = {}
            for k, v in kwargs.items():
                if k in kwarg_map:
                    deprecated_statement = f"was deprecated in version {deprecated_since}" if deprecated_since else "has been deprecated"
                    removal_statement = f" and is scheduled to be removed in version/on date {removal_when}\n" if removal_when else ""
                    message = (
                        f"In {func.__name__}(): argument '{k}' {deprecated_statement}\n"
                        f"{removal_statement}"
                        f"Please update your code to use '{kwarg_map[k]}={v}' instead."
                    )
                    warnings.warn(
                        message, DeprecationWarning, stacklevel=2
                    )
                new_kwargs[kwarg_map.get(k, k)] = v
            return func(*args, **new_kwargs)
        return wrapped
    return decorator

def deprecated_attribute(old_attr, new_attr, deprecated_since: str=None, removal_when: str=None):
    def decorator(cls):
        @property
        def deprecated_prop(self):
            deprecated_statement = f"was deprecated in version {deprecated_since}" if deprecated_since else "has been deprecated"
            removal_statement = f" and is scheduled to be removed in version/on date {removal_when}\n" if removal_when else ""
            message = (
                f"Attribute '{old_attr}' on {cls.__name__} {deprecated_statement}\n"
                f"{removal_statement}"
                f"Please update your code to use '{new_attr}' instead."
            )
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            return getattr(self, new_attr)

        @deprecated_prop.setter
        def deprecated_prop(self, value):
            deprecated_statement = f"was deprecated in version {deprecated_since}" if deprecated_since else "has been deprecated"
            removal_statement = f" and is scheduled to be removed in version/on date {removal_when}\n" if removal_when else ""
            message = (
                f"Attribute '{old_attr}' on {cls.__name__} {deprecated_statement}\n"
                f"{removal_statement}"
                f"Please update your code to use '{new_attr}' instead."
            )
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            setattr(self, new_attr, value)

        setattr(cls, old_attr, deprecated_prop)
        return cls
    return decorator

class _ClassProperty(object):
    def __init__(self, fget, fset):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, owner):
        return self.fget(owner)

    def __set__(self, owner, value):
        self.fset(owner, value)

def deprecated_class_attribute(old_attr, new_attr, deprecated_since: str=None, removal_when: str=None):
    def decorator(cls):
        def getter(owner_cls):
            deprecated_statement = f"was deprecated in version {deprecated_since}" if deprecated_since else "has been deprecated"
            removal_statement = f" and is scheduled to be removed in version/on date {removal_when}\n" if removal_when else ""
            message = (
                f"Class attribute '{old_attr}' on {owner_cls.__name__} {deprecated_statement}\n"
                f"{removal_statement}"
                f"Please update your code to use '{new_attr}' instead."
            )
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            return getattr(owner_cls, new_attr)

        def setter(owner_cls, value):
            deprecated_statement = f"was deprecated in version {deprecated_since}" if deprecated_since else "has been deprecated"
            removal_statement = f" and is scheduled to be removed in version/on date {removal_when}\n" if removal_when else ""
            message = (
                f"Class attribute '{old_attr}' on {owner_cls.__name__} {deprecated_statement}\n"
                f"{removal_statement}"
                f"Please update your code to use '{new_attr}' instead."
            )
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            setattr(owner_cls, new_attr, value)
        
        setattr(cls, old_attr, _ClassProperty(getter, setter))
        return cls
    return decorator

def create_deprecation_handlers(module_name, module_globals, deprecation_map):
    """
    Factory function that creates PEP 562-compliant __getattr__
    and __dir__ functions for a specific module.

    Args:
        module_name (str): The __name__ of the calling module.
        module_globals (dict): The globals() of the calling module.
        deprecation_map (dict): The map of deprecated names for that module.

    Returns:
        (function, function): A tuple containing the
                              generated __getattr__ and __dir__ functions.
    """

    # This inner function will become __getattr__
    def _getattr(name):
        if name in deprecation_map:
            info = deprecation_map[name]
            new_name = info["new_name"]

            # Check that the new name actually exists in the module
            if new_name not in module_globals:
                raise ImportError(
                    f"Deprecation import failed: '{name}' points to "
                    f"'{new_name}', which is not in {module_name}."
                )

            # Issue the warning
            warnings.warn(
                f"Module '{module_name}': '{name}' is deprecated since v{info['deprecated_since']} "
                f"and will be removed in v{info['removal_when']}. "
                f"Please use '{info['new_name']}' instead.",
                DeprecationWarning,
                stacklevel=2
            )

            # Return the *actual* new object from the module's scope
            return module_globals[new_name]

        raise AttributeError(f"module '{module_name}' has no attribute '{name}'")

    # This inner function will become __dir__
    def _dir():
        # Get all "real" module attributes and add the "fake" deprecated ones
        return list(module_globals.keys()) + list(deprecation_map.keys())

    # Return the two functions that will be assigned
    return _getattr, _dir


#def removed_arg(kwarg_map: dict, removed_in: str=None):
#    def decorator(func):
#        def wrapped(*args, **kwargs):
#            for k in kwargs.keys():
#                if k in kwarg_map:
#                    removed_statement = f"was removed in version {removed_in}" if removed_in else "has been removed"
#                    message = (
#                        f"In {func.__name__}(): argument '{k}' {removed_statement}\n"
#                        f"Please update your code to use '{kwarg_map[k]}' instead."
#                    )
#                    raise TypeError(message)
#            return func(*args, **kwargs)
#        return wrapped
#    return decorator
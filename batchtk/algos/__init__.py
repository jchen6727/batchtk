import importlib.util
# check before import 2/2 reliance on non-core dependencies...

def missing_dependency(*args, **kwargs):
    raise ImportError("This function requires optional package dependencies that are not installed. Please refer to the relevant .py and install them prior to running this function.")

if importlib.util.find_spec('smac'):
    from .smac_utils import *
else:
    smac_search = missing_dependency

if importlib.util.find_spec('optuna'):
    from .optuna_utils import *
else:
    optuna_search = missing_dependency

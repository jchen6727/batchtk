#import importlib.util
# check before import 2/2 reliance on non-core dependencies...

from utils import Trial

def missing_dependency(*args, **kwargs):
    raise ImportError("This algorithm requires optional package dependencies that are not installed. Please refer to the relevant .py and install them prior to running this function.")

try:
    from .smac_utils import *
except Exception as e:
    smac_search = missing_dependency

try:
    from .optuna_utils import *
except Exception as e:
    optuna_search = missing_dependency

try:
    from .cmaes_utils import *
except Exception as e:
    cmaes_search = missing_dependency

try:
    from .salib_utils import *
except Exception as e:
    salib_search = missing_dependency


"""
if importlib.util.find_spec('smac'):
    from .smac_utils import *
else:
    smac_search = missing_dependency

if importlib.util.find_spec('optuna'):
    from .optuna_utils import *
else:
    optuna_search = missing_dependency
"""
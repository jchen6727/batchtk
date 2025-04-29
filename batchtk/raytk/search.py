import pandas
from ray import tune
import types
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from batchtk.runtk.trial import trial, LABEL_POINTER, PATH_POINTER
def ray_trial(config, label, dispatcher_constructor, project_path, output_path, submit_constructor, dispatcher_kwargs=None, submit_kwargs=None, interval=60, log=None, report=('path', 'config', 'data')):
    tid = tune.get_context().get_trial_id()
    tid = tid.split('_')[-1]  # value for trial (can be int/string)
    return trial(config, label, tid, dispatcher_constructor, project_path, output_path, submit_constructor, dispatcher_kwargs, submit_kwargs, interval=interval, log=log, report=report)

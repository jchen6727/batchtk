import ray
import pandas
from ray import train
import types
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from batchtk.runtk.trial import trial, LABEL_POINTER, PATH_POINTER
def ray_trial(config, label, dispatcher_constructor, project_path, output_path, submit, dispatcher_kwargs=None, interval=60):
    tid = ray.train.get_context().get_trial_id()
    tid = tid.split('_')[-1]  # value for trial (can be int/string)
    return trial(config, label, tid, dispatcher_constructor, project_path, output_path, submit, dispatcher_kwargs, interval=interval)

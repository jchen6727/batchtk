import pandas
from ray import tune
import types
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from batchtk.runtk.trial import trial, LABEL_POINTER, PATH_POINTER
from batchtk import runtk

def ray_trial(config, label, dispatcher_constructor, project_path, output_path, submit_constructor, dispatcher_kwargs=None, submit_kwargs=None, interval=60, data_storage=None, debug_log=None, report=('path', 'config', 'data'),
              cleanup=(runtk.SGLOUT, runtk.MSGOUT), check_storage=True):
    tid = tune.get_context().get_trial_id()
    tid = tid.split('_')[-1]  # value for trial (can be int/string)
    return trial(
        config=config, label=label, tid=tid, dispatcher_constructor=dispatcher_constructor,
        project_path=project_path, output_path=output_path, submit_constructor=submit_constructor,
        dispatcher_kwargs=dispatcher_kwargs, submit_kwargs=submit_kwargs, interval=interval,
        data_storage=data_storage, debug_log=debug_log, report=report, cleanup=cleanup, check_storage=check_storage)

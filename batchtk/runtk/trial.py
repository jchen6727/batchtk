import types
import pandas
from io import StringIO
from batchtk.utils import DataLogger
import json
import warnings
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


def trials(configs, label, gen, dispatcher_constructor, project_path, output_path, submit_constructor, dispatcher_kwargs=None, submit_kwargs=None, interval=60, log=None, report=('path', 'config', 'data')):
    label = '{}_{}'.format(label, gen)
    results = []
    for tid, config in enumerate(configs):
        results.append(trial(config, label, tid, dispatcher_constructor, project_path, output_path, submit_constructor, dispatcher_kwargs, submit_kwargs, interval, log, report))
    return results

def trial(config: Dict, label: str, tid: [str|int], dispatcher_constructor: callable, project_path: str,
          output_path: str, submit_constructor: callable, dispatcher_kwargs: Optional[dict] =None,
          submit_kwargs: Optional[dict] =None, interval: Optional[int]=60, log=None, report=('path', 'config', 'data')):
    """
    Run a single trial:
    config: dict - parameter configuration for the trial (variables to be passed by the dispatcher to the receiving script)
    label: str - label for a set of trials (see trials)
    tid: str or int - trial id unique to this single trial
    dispatcher_constructor: callable - dispatcher class to be used for this trial
    project_path: str - path to the project directory
    output_path: str - path to the output directory
    submit_constructor: callable - submit class to be used for this trial
    dispatcher_kwargs: dict - kwargs to be passed to the dispatcher constructor
    submit_kwargs: dict - kwargs to be passed to the submit templates
    interval: int - interval for the dispatcher to check for messages
    log: DataLogger - data logger to be used for this trial 
    report: tuple - options/order (left -> right update calls) for the data to be returned
    """
    dispatcher_kwargs = dispatcher_kwargs or {}
    submit_kwargs = submit_kwargs or {}
    submit = submit_constructor()
    submit.update_templates(**submit_kwargs)
    run_label = '{}_{}'.format(label, tid)
    trial.run_label = run_label
    trial.output_path = output_path
    for k, v in config.items(): #call any function pointers
        if isinstance(v, types.FunctionType):
            config[k] = v()
    dispatcher = dispatcher_constructor(project_path=project_path, output_path=output_path, submit=submit,
                                        label=run_label, **dispatcher_kwargs)
    dispatcher.update_env(dictionary=config)
    try:
        dispatcher.start()
        dispatcher.connect()
        msg = json.loads(dispatcher.recv(interval=interval))
        dispatcher.clean()
    except Exception as e:
        dispatcher.clean()
        raise (e)
    data = {}
    data_options = {
        'path': {'trial_label': run_label, 'trial_path': dispatcher.output_path},
        'config': config,
        'data': msg,
    }

    for option in report:
        try:
            data.update(data_options[option])
        except KeyError:
            warnings.warn('{} not in report options'.format(option))

    if isinstance(log, DataLogger):
        log.log(data)

    def _lctf(val):
        """internal loose cast, converts to float if possible, o/w returns same"""
        try:
            return float(val)
        except:
            return val
    data = pandas.Series(data)
    data = data.apply(_lctf)
    return data


LABEL_POINTER = lambda:trial.run_label
PATH_POINTER = lambda:trial.output_path
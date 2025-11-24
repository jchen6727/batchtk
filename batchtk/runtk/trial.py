import types
import pandas
from io import StringIO
from batchtk.utils import SQLStorage, create_logger, Storage
from logging import Logger
from batchtk import runtk # handles
import json
import warnings
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from batchtk.utils.version import deprecated_arg, create_deprecation_handlers

_DEPRECATED = {
    "PATH_POINTER": {
        "deprecated_since": "0.1.7",
        "removal_when": "0.1.9",
        "new_name": "DIR_POINTER",
    }
}
__getattr__, __dir__ = create_deprecation_handlers(
    module_name=__name__,
    module_globals=globals(),
    deprecation_map=_DEPRECATED,
)

@deprecated_arg({"output_path": "output_dir", "project_path": "project_dir"}, deprecated_since="0.1.7", removal_when="0.1.9")
def trials(configs, label, gen, dispatcher_constructor, project_dir, output_dir, submit_constructor, dispatcher_kwargs=None, submit_kwargs=None, interval=60, log=None, report=('path', 'config', 'data'), cleanup=True):
    label = '{}_{}'.format(label, gen)
    results = []
    for tid, config in enumerate(configs):
        results.append(trial(config, label, tid, dispatcher_constructor, project_dir, output_dir, submit_constructor, dispatcher_kwargs, submit_kwargs, interval, log, report))
    return results

def _lctf(val):
    """internal loose cast, converts to float if possible, o/w returns same"""
    try:
        return float(val)
    except:
        return val

@deprecated_arg({"output_path": "output_dir", "project_path": "project_dir", "data_storage": "storage_constructor", }, deprecated_since="0.1.7", removal_when="0.1.9")
def trial(config: dict, label: str, tid: [str|int], dispatcher_constructor: callable, project_dir: str,
          output_dir: str, submit_constructor: callable, checkpoint_dir: Optional[str] = None, dispatcher_kwargs: Optional[dict] =None,
          submit_kwargs: Optional[dict] =None, interval: Optional[int]=60, storage_constructor: Optional[callable]=None, storage_kwargs: Optional[dict] = None,
          debug_log: Optional[Logger|str]=None, report: Optional[list]=('path', 'config', 'data'), cleanup: Optional[bool|list|tuple] = (runtk.SGLOUT, runtk.MSGOUT), check_storage: Optional[bool]=True, **kwargs) -> pandas.Series:
    """
    Run a single trial:
    config: dict - parameter configuration for the trial (variables to be passed by the dispatcher to the receiving script)
    label: str - label for a set of trials (see trials)
    tid: str or int - trial id unique to this single trial
    dispatcher_constructor: callable - dispatcher class to be used for this trial
    project_dir: str - path to the project directory
    output_dir: str - path to the output directory
    submit_constructor: callable - submit class to be used for this trial
    dispatcher_kwargs: dict - kwargs to be passed to the dispatcher constructor
    submit_kwargs: dict - kwargs to be passed to the submit templates
    interval: int - interval for the dispatcher to check for messages
    data_storage: Storage - data storage for trial results
    debug_log: Logger - logger used for debug output
    report: tuple - options/order (left -> right update calls) for the data to be returned
    cleanup: bool or list/tuple - (True -> clean all files) clean up associated trial handles after a trial is completed.
    check_storage: bool - use the passed data_storage as a checkpoint for the trial, if trial data exists with a matching <label>_<tid>, then the trial is skipped and the stored data is pulled from check_storage.
    """
    dispatcher_kwargs = dispatcher_kwargs or {}
    submit_kwargs = submit_kwargs or {}
    submit = submit_constructor()
    submit.update_templates(**submit_kwargs)
    run_label = '{}_{}'.format(label, tid)
    trial.run_label = run_label
    trial.output_dir = output_dir
    if not debug_log:
        debug_log = create_logger(file_out=False) # only use debug_log for warning level prints to console --
    if isinstance(debug_log, str) or isinstance(debug_log, bool):
        debug_log = create_logger(name='batchtk', file_out=debug_log)
    assert isinstance(debug_log, Logger)
    for k, v in config.items(): #assign values to pointers/future values referenced in config.
        if isinstance(v, types.FunctionType):
            config[k] = v()
    if storage_constructor:
        storage_kwargs = storage_kwargs or {'directory': checkpoint_dir or project_dir,
                                            'label': label}
    data_storage = storage_constructor()
    data_storage_enabled = isinstance(data_storage, Storage)
    if check_storage:
        data = None
        if not data_storage_enabled:
            debug_log.warning('No valid batchtk data_storage object provided for internal checkpointing (external checkpointing may exist), skipping internal check_storage operations.')
        else:
            try:
                data = data_storage.find(key='trial_label', value=run_label)
            except ValueError: # this is not the ONLY error --
                debug_log.warning("trial_label not a column in the log database, skipping log check (recommend passing at least: ('path', 'data') to arguments).")
            except Exception as e:
                debug_log.warning("checking log database failed due to error: {}, skipping log check.".format(e))
        if data is not None: # skip the trail if trial_label: run_label already exists in the log database.
            debug_log.info("trial_label already exists in the log database, skipping trial and retrieved data: {}.".format(data))
            return data.apply(_lctf)

    dispatcher = dispatcher_constructor(project_dir=project_dir, output_dir=output_dir, submit=submit,
                                        label=run_label, **dispatcher_kwargs)
    dispatcher.update_env(dictionary=config)
    try:
        dispatcher.start()
        dispatcher.connect()
        msg = json.loads(dispatcher.recv(interval=interval))
        dispatcher.clean() # don't do a file cleanup here, wait until successful conversion of data.
        # -> i.e., what happens if error occurs during subsequent calls.
    except Exception as e:
        dispatcher.clean() # don't delete files on an exception
        dispatcher.close()
        raise (e)
    data = {}
    data_options = {
        'path': {'trial_label': run_label, 'trial_dir': dispatcher.output_dir}, #nomenclature decided in e54413e. "path" and "label" overlaps with config.
        'config': config,
        'data': msg,
    }
    debug_log.warning("message received: {}".format(msg))
    for option in report:
        try:
            data.update(data_options[option])
        except KeyError:
            debug_log.warning('{} not in report options'.format(option))
    if data_storage_enabled:
        debug_log.warning("inserting data into storage: {}".format(data))

        data_storage.insert(data)
    data = pandas.Series(data)
    data = data.apply(_lctf)
    dispatcher.clean(handles=cleanup)
    dispatcher.close()
    return data


LABEL_POINTER = lambda:trial.run_label

#@deprecated(version="0.1.6", reason="trial.PATH_POINTER replaced with trial.DIR_POINTER.")
#def PATH_POINTER():
#    return trial.output_dir
#PATH_POINTER = lambda:trial.output_dir

DIR_POINTER = lambda:trial.output_dir
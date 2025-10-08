import types
import pandas
from io import StringIO
from batchtk.utils import SQLStorage, ScriptLogger, Storage
from logging import Logger
from batchtk import runtk # handles
import json
import warnings
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


def trials(configs, label, gen, dispatcher_constructor, project_path, output_path, submit_constructor, dispatcher_kwargs=None, submit_kwargs=None, interval=60, log=None, report=('path', 'config', 'data'), cleanup=True):
    label = '{}_{}'.format(label, gen)
    results = []
    for tid, config in enumerate(configs):
        results.append(trial(config, label, tid, dispatcher_constructor, project_path, output_path, submit_constructor, dispatcher_kwargs, submit_kwargs, interval, log, report))
    return results

def _lctf(val):
    """internal loose cast, converts to float if possible, o/w returns same"""
    try:
        return float(val)
    except:
        return val

def trial(config: dict, label: str, tid: [str|int], dispatcher_constructor: callable, project_path: str,
          output_path: str, submit_constructor: callable, dispatcher_kwargs: Optional[dict] =None,
          submit_kwargs: Optional[dict] =None, interval: Optional[int]=60, data_storage: Optional[Storage]=None,
          debug_log: Optional[Logger|str]=None, report: Optional[list]=('path', 'config', 'data'), cleanup: Optional[bool|list|tuple] = (runtk.SGLOUT, runtk.MSGOUT), check_storage: Optional[bool]=True) -> pandas.Series:
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
    trial.output_path = output_path
    if not debug_log:
        debug_log = ScriptLogger(file_out=False) # only use debug_log for warning level prints to console --
    if isinstance(debug_log, str) or isinstance(debug_log, bool):
        debug_log = ScriptLogger(name='batchtk', file_out=debug_log)
    assert isinstance(debug_log, Logger)
    for k, v in config.items(): #assign values to pointers/future values referenced in config.
        if isinstance(v, types.FunctionType):
            config[k] = v()
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

    dispatcher = dispatcher_constructor(project_path=project_path, output_path=output_path, submit=submit,
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
        'path': {'trial_label': run_label, 'trial_path': dispatcher.output_path}, #nomenclature decided in e54413e. "path" and "label" overlaps with config.
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
PATH_POINTER = lambda:trial.output_path
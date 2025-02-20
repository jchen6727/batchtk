import types
import pandas
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
def trials(configs, label, gen, dispatcher_constructor, project_path, output_path, submit, dispatcher_kwargs=None, interval=60):
    label = '{}_{}'.format(label, gen)
    results = []
    for tid, config in enumerate(configs):
        results.append(trial(config, label, tid, dispatcher_constructor, project_path, output_path, submit, dispatcher_kwargs, interval))
    return results


def trial(config, label, tid, dispatcher_constructor, project_path, output_path, submit, dispatcher_kwargs=None, interval=60):
    dispatcher_kwargs = dispatcher_kwargs or {}
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
        data = dispatcher.recv(interval=interval)
        dispatcher.clean()
    except Exception as e:
        dispatcher.clean()
        raise (e)
    data = pandas.read_json(data, typ='series', dtype=float)
    return data


LABEL_POINTER = lambda:trial.run_label
PATH_POINTER = lambda:trial.output_path
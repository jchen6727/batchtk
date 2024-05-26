import types
import pandas

from typing import Any, Callable, Dict, List, Optional, Tuple, Union
def trials(configs, label, gen, dispatcher_constructor, project_path, output_path, submit):
    label = '{}_{}'.format(label, gen)
    results = []
    for tid, config in enumerate(configs):
        results.append(trial(config, label, tid, dispatcher_constructor, project_path, output_path, submit))
    return results


def trial(config, label, tid, dispatcher_constructor, project_path, output_path, submit):
    run_label = '{}_{}'.format(label, tid)
    trial.run_label = run_label
    trial.output_path = output_path
    for k, v in config.items(): #call any function pointers
        if isinstance(v, types.FunctionType):
            config[k] = v()
    dispatcher = dispatcher_constructor(project_path=project_path, output_path=output_path, submit=submit,
                                        gid=run_label)
    dispatcher.update_env(dictionary=config)
    try:
        dispatcher.run()
        dispatcher.accept()
        data = dispatcher.recv()
        dispatcher.clean()
    except Exception as e:
        dispatcher.clean()
        raise (e)
    data = pandas.read_json(data, typ='series', dtype=float)
    return data


LABEL_POINTER = lambda:trial.run_label


PATH_POINTER = lambda:trial.output_path
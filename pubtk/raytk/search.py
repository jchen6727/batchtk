import ray
import pandas
from ray import train
import types


def ray_trial(config, label, dispatcher_constructor, project_path, output_path, submit):
    tid = ray.train.get_context().get_trial_id()
    tid = tid.split('_')[-1]  # value for trial (can be int/string)
    run_label = '{}_{}'.format(label, tid)
    ray_trial.run_label = run_label
    ray_trial.output_path = output_path
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

LABEL_POINTER = lambda:ray_trial.run_label
PATH_POINTER = lambda:ray_trial.output_path

#TODO do we want any other variables pulled from the function?
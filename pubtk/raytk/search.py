import ray
import pandas
import os
from ray import tune, train
from ray.air import session, RunConfig
from ray.tune.search import create_searcher, ConcurrencyLimiter, SEARCH_ALG_IMPORT
from collections import namedtuple
import types



def get_path(path):
    if path[0] == '/':
        return os.path.normpath(path)
    elif path[0] == '.':
        return os.path.normpath(os.path.join(os.getcwd(), path))
    else:
        raise ValueError("path must be an absolute path (starts with /) or relative to the current working directory (starts with .)")


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


def ray_search(dispatcher_constructor, submit_constructor, algorithm = "variant_generator", label = 'search',
               params = None, output_path = '../batch', checkpoint_path = '../ray',
               batch_config = None, num_samples = 1, metric = "loss", mode = "min", algorithm_config = None):
    ray.init(runtime_env={"working_dir": "."}) # TODO needed for python import statements ?

    if algorithm_config == None:
        algorithm_config = {}

    if 'metric' in algorithm_config:
        metric = algorithm_config['metric']
    else:
        metric = None

    if 'mode' in algorithm_config:
        mode = algorithm_config['mode']
    else:
        mode = None
    #TODO class this object for self calls? cleaner? vs nested functions
    #TODO clean up working_dir and excludes
    storage_path = get_path(checkpoint_path)
    algo = create_searcher(algorithm, **algorithm_config) #concurrency may not be accepted by all algo
    #search_alg – The search algorithm to use.
    #  metric – The training result objective value attribute. Stopping procedures will use this attribute.
    #  mode – One of {min, max}. Determines whether objective is minimizing or maximizing the metric attribute.
    #  **kwargs – Additional parameters. These keyword arguments will be passed to the initialization function of the chosen class.
    try:
        algo = ConcurrencyLimiter(searcher=algo, max_concurrent=algorithm_config['max_concurrent'], batch=algorithm_config['batch'])
    except:
        pass

    submit = submit_constructor()
    submit.update_templates(
        **batch_config
    )
    project_path = os.getcwd()
    def run(config):
        data = ray_trial(config, label, dispatcher_constructor, project_path, output_path, submit)
        if isinstance(metric, str):
            metrics = {'config': config, 'data': data, metric: data[metric]}
            session.report(metrics)
        elif isinstance(metric, (list, tuple)):
            metrics = {k: data[k] for k in metric}
            metrics['data'] = data
            metrics['config'] = config
            session.report(metrics)
        else:
            session.report({'data': data, 'config': config})

    tuner = tune.Tuner(
        run,
        tune_config=tune.TuneConfig(
            search_alg=algo,
            num_samples=num_samples, # grid search samples 1 for each param
            metric="data"
        ),
        run_config=RunConfig(
            storage_path=storage_path,
            name=algorithm,
        ),
        param_space=params,
    )

    results = tuner.fit()
    resultsdf = results.get_dataframe()
    resultsdf.to_csv("{}.csv".format(label))

"""
Parameters
:
space –
Hyperparameter search space definition for Optuna’s sampler. This can be either a dict with parameter names as keys and optuna.distributions as values, or a Callable - in which case, it should be a define-by-run function using optuna.trial to obtain the hyperparameter values. The function should return either a dict of constant values with names as keys, or None. For more information, see https://optuna.readthedocs.io/en/stable/tutorial/10_key_features/002_configurations.html.
Warning
No actual computation should take place in the define-by-run function. Instead, put the training logic inside the function or class trainable passed to tune.Tuner().
metric – The training result objective value attribute. If None but a mode was passed, the anonymous metric _metric will be used per default. Can be a list of metrics for multi-objective optimization.
mode – One of {min, max}. Determines whether objective is minimizing or maximizing the metric attribute. Can be a list of modes for multi-objective optimization (corresponding to metric).
points_to_evaluate – Initial parameter suggestions to be run first. This is for when you already have some good parameters you want to run first to help the algorithm make better suggestions for future parameters. Needs to be a list of dicts containing the configurations.
sampler –
Optuna sampler used to draw hyperparameter configurations. Defaults to MOTPESampler for multi-objective optimization with Optuna<2.9.0, and TPESampler in every other case. See https://optuna.readthedocs.io/en/stable/reference/samplers/index.html for available Optuna samplers.
Warning
Please note that with Optuna 2.10.0 and earlier default MOTPESampler/TPESampler suffer from performance issues when dealing with a large number of completed trials (approx. >100). This will manifest as a delay when suggesting new configurations. This is an Optuna issue and may be fixed in a future Optuna release.
seed – Seed to initialize sampler with. This parameter is only used when sampler=None. In all other cases, the sampler you pass should be initialized with the seed already.
evaluated_rewards –
If you have previously evaluated the parameters passed in as points_to_evaluate you can avoid re-running those trials by passing in the reward attributes as a list so the optimiser can be told the results without needing to re-compute the trial. Must be the same length as points_to_evaluate.

"""
def ray_optuna_search(dispatcher_constructor, submit_constructor, label = 'optuna_search',
                      params = None, output_path = '../batch', checkpoint_path = '../ray',
                      batch_config = None, max_concurrent = 1, batch = True, num_samples = 1,
                      metric = "loss", mode = "min", optuna_config = None):
    """
    ray_optuna_search(dispatcher_constructor, submit_constructor, label,
                      params, output_path, checkpoint_path,
                      batch_config, max_concurrent, batch, num_samples,
                      metric, mode, optuna_config)
    Parameters
    ----------
    dispatcher_constructor
    submit_constructor
    label
    params
    output_path
    checkpoint_path
    batch_config
    max_concurrent
    batch
    num_samples
    metric
    mode
    optuna_config

    Returns
    -------
    """
    from ray.tune.search.optuna import OptunaSearch

    ray.init(runtime_env={"working_dir": "."})# TODO needed for python import statements ?
    if optuna_config == None:
        optuna_config = {}

    storage_path = get_path(checkpoint_path)
    algo = ConcurrencyLimiter(searcher=OptunaSearch(metric=metric, mode=mode, **optuna_config),
                              max_concurrent=max_concurrent,
                              batch=batch) #TODO does max_concurrent and batch work?

    submit = submit_constructor()
    submit.update_templates(
        **batch_config
    )
    project_path = os.getcwd()

    def run(config):
        data = ray_trial(config, label, dispatcher_constructor, project_path, output_path, submit)
        if isinstance(metric, str):
            metrics = {'config': config, 'data': data, metric: data[metric]}
            session.report(metrics)
        elif isinstance(metric, (list, tuple)):
            metrics = {k: data[k] for k in metric}
            metrics['config'] = config
            metrics['data'] = data
            session.report(metrics)
        else:
            raise ValueError("metric must be a string or a list/tuple of strings")

    tuner = tune.Tuner(
        run,
        tune_config=tune.TuneConfig(
            search_alg=algo,
            num_samples=num_samples,
        ),
        run_config=RunConfig(
            storage_path=storage_path,
            name=label,
        ),
        param_space=params,
    )

    results = tuner.fit()
    resultsdf = results.get_dataframe()
    resultsdf.to_csv("{}.csv".format(label))
    return namedtuple('Study', ['algo', 'results'])(algo, results)


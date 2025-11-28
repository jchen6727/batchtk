import cmaes

from batchtk.utils import SQLStorage, SQLiteStorage, create_logger, expand_path
from batchtk.runtk.trial import trial as runtk_trial
from batchtk.runtk import constructors

import pandas
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from batchtk import runtk
import numpy
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor



from batchtk.runtk.trial import trial as runtk_trial

from batchtk.runtk.trial import LABEL_POINTER, DIR_POINTER

from logging import Logger

from batchtk.utils.version import deprecated_arg, create_deprecation_handlers

_SAMPLERS = { # refer #https://github.com/CyberAgentAILab/cmaes/tree/main
    'base': cmaes.CMA,
    'margin': cmaes.CatCMAwM,
}

_futuretuple = namedtuple('FutureTuple', ['id', 'future', 'vals', 'cfg'])

def _xzc_to_cfg(x_names, z_names, c_names, x_vals, z_vals, c_bools, c_vals):
    cfg = {}
    if x_vals is not None:
        for name, val in zip(x_names, x_vals):
            cfg[name] = val
    if z_vals is not None:
        for name, val in zip(z_names, z_vals):
            cfg[name] = val
    if c_vals is not None:
        for name, bools, vals in zip(c_names, c_bools, c_vals):
            #final = [val if _bool else None for val, _bool in zip(vals, onehot)]
            # but onehot through numpy cleaner---
            index = numpy.argmax(bools)
            cfg[name] = vals[index]
    return cfg

@deprecated_arg({"output_path": "output_dir", "project_path": "project_dir"}, deprecated_since="0.1.7", removal_when="0.1.9")
def cmaes_search(
    # algo args
    study_label: str = None, param_space: dict = None, metrics: dict = None,
    param_space_samplers = None, num_trials: int = 0, num_workers: int = None,
    algo: Optional[str] = 'base', algo_kwargs: Optional[dict] = None,
    seed: Optional[int] = None,
    # trial args
    dispatcher_constructor: callable = None, project_dir: str = None,
    output_dir: str = None, submit_constructor: callable = None,
    checkpoint_dir: str =None, dispatcher_kwargs: Optional[dict] = None,
    submit_kwargs : Optional[dict] = None, interval: Optional[int] = 60,
    storage_constructor: Optional[callable] = constructors.SQLiteStorage,
    log_constructor: Optional[callable]=constructors.BatchtkLogger,
    log_kwargs: Optional[dict] = None, report: Optional[list] = ('path', 'config', 'data'),
    cleanup: Optional[bool | list | tuple] = (runtk.SGLOUT, runtk.MSGOUT),
    check_storage: Optional[bool] = True, ** kwargs) -> dict:
    """
    Perform an optimization search using CMAES.
    study_label: str - label for the study (used in storage and logging)
    param_space: dict - dictionary defining the parameter search space, keys are parameter names and values are tuples defining (lower_bound, upper_bound)
    metrics: dict - dictionary defining the metrics to optimize and the direction of optimization, keys are metric names and values are 'minimize' (search for lowest value) or 'maximize' (search for highest value)
    param_space_samplers: list - list of strings defining the sampler for each parameter in param_space, one of 'categorical', 'int', or 'float' (defaults to 'float' for all parameters)
    num_trials: int - number of trials to run
    num_workers: int - number of trials to be run in parallel (uses multiprocessing)
    dispatcher_constructor: callable - calling function to a dispatcher class -- see dispatchers.py
    project_dir: str - path to the project directory containing the source code to be executed
    output_dir: str - path to the output directory where runtime files, results and logs will be stored
    submit_constructor: callable - calling function to a submit class -- see submits.py
    algo: str - optimization algorithm to use, one of 'nsgaii', 'random', 'tspe' (defaults to tspe for single objective, nsgaii for multi-objective)
    algo_kwargs: dict - additional keyword arguments to pass to the optimization algorithm constructor
    seed: int - random seed for the optimization algorithm (default None uses a random seed)
    dispatcher_kwargs: dict - additional keyword arguments to pass to the dispatcher constructor
    submit_kwargs: dict - additional keyword arguments to format the submission script.
    interval: int - time interval (in seconds) between polling for completed trials
    data_storage: SQLStorage - instance of a SQLStorage class to store trial data (optuna also keeps its own storage)
    debug_log: Logger - instance of a Logger class, default will only print warnings to console
    report: list - list of strings ('path', 'config', 'data') defining values to be written to data_storage if it exists.
    cleanup: bool | list | tuple - whether to cleanup runtime files (if bool is supplied), or a sequence of handles (runtk.SGLOUT, runtk.MSGOUT...) to cleanup upon successful trial completion
    check_storage: bool - whether to check data_storage for existing trials and skip if found (only if data_storage is provided)
    """

    # set up debug_log first...
    log_kwargs = log_kwargs or {'file_out': f"{project_dir}/{study_label}.log"}
    if log_constructor:
        try:
            debug_log = log_constructor(**log_kwargs)
            assert isinstance(debug_log, Logger)
        except Exception as e:
            raise ValueError(
                f"log_constructor {log_constructor} must return an instance of class Logger when called with **log_kwargs {log_kwargs}, instead encountered error: {e}.")
    else:
        debug_log = None

    algo_kwargs = algo_kwargs or {}
    bounds = []
    if not all(sampler in ('categorical', 'int', 'float') for sampler in param_space_samplers):
        raise ValueError("all param_space_samplers must be one of 'categorical', 'int', or 'float'")
    if any(sampler in ('categorical', 'int') for sampler in param_space_samplers) or algo == 'margin':
        if algo != 'margin':
            debug_log.warn("categorical and Integer sampling detected in param_space, using margin sampler.")
            algo = 'margin'
        x_names = []
        c_names = []
        z_names = []
        c_choices = []
        for key in ('x_space', 'z_space', 'c_space'):
            algo_kwargs[key] = []
        for i, (key, args) in enumerate(param_space.items()):
            if param_space_samplers[i] == 'float':
                x_names.append(key)
                algo_kwargs['x_space'].append([args[0], args[1]])
                bounds.append(args)
            if param_space_samplers[i] == 'int':
                z_names.append(key)
                algo_kwargs['z_space'].append([args[0], args[1]])
                bounds.append(args)
            if param_space_samplers[i] == 'categorical':
                c_names.append(key)
                algo_kwargs['c_space'].append(len(args))
                c_choices.append(args)
        for key in ('x_space', 'z_space', 'c_space'):
            if len(algo_kwargs[key]) == 0:
                del algo_kwargs[key]
    else:
        names = []
        midpoints = []
        for keys, args in param_space.items():
            names.append(keys)
            midpoints.append( (args[0]+args[1]) / 2.0)
            bounds.append([args[0], args[1]])
        if 'mean' not in algo_kwargs: algo_kwargs['mean'] = numpy.array(midpoints)
        if 'bounds' not in algo_kwargs: algo_kwargs['bounds'] = numpy.array(bounds)

    if 'sigma' not in algo_kwargs and bounds: #or len(bounds) > 0
        algo_kwargs['sigma'] = 0
        for low, high in bounds:
            algo_kwargs['sigma'] += (high - low)/4
        algo_kwargs['sigma'] /= len(bounds) # rough estimate of 1/4 the average range of parameters.

    if seed:
        algo_kwargs['seed'] = seed

    if num_workers is not None:
        algo_kwargs['population_size'] = num_workers

    # call
    debug_log.warn("cmaes search with the following meta-parameters:\n{}".format(algo_kwargs))
    sampler = _SAMPLERS[algo](**algo_kwargs)
    num_generations = int(numpy.ceil(num_trials / sampler.population_size))
    key = list(metrics.keys())[0] # currently only support single objective

    def eval_trial(cfg, tid):
        cfg['_batchtk_label_pointer'] = LABEL_POINTER
        cfg['_batchtk_path_pointer'] = DIR_POINTER
        loss = runtk_trial(
            config=cfg,
            label=study_label,
            tid=tid,
            dispatcher_constructor=dispatcher_constructor,
            project_dir=project_dir,
            output_dir=output_dir,
            submit_constructor=submit_constructor,
            checkpoint_dir=checkpoint_dir,
            dispatcher_kwargs=dispatcher_kwargs,
            submit_kwargs=submit_kwargs,
            interval=interval,
            storage_constructor=storage_constructor,
            log_constructor=log_constructor,
            log_kwargs=log_kwargs,
            report=report,
            cleanup=cleanup,
            check_storage=check_storage
        )
        return float(loss[key])
    gens_summary = {}
    best = (None, numpy.inf)
    for gen in range(num_generations):
        solutions = []
        futures = []
        with ThreadPoolExecutor(max_workers=sampler.population_size) as executor:
            for cand in range(sampler.population_size):
                if algo == 'margin':
                    vals = sampler.ask()
                    x_vals, z_vals, c_bools = vals.x, vals.z, vals.c
                    cfg = _xzc_to_cfg(x_names, z_names, c_names, x_vals, z_vals, c_bools, c_choices)
                else:
                    vals = sampler.ask()
                    cfg = {name: val for name, val in zip(names, vals)}
                tid = "{}_{}".format(gen, cand)
                futures.append(_futuretuple(id=tid,
                                            future=executor.submit(eval_trial, cfg=cfg, tid=tid),
                                            vals=vals,
                                            cfg=cfg))
            for future in futures:
                loss = future.future.result()
                if loss < best[1]:
                    best = (future.cfg, loss)
                solutions.append((future.vals, loss))
                gens_summary[future.id] = {'config': future.cfg, 'loss': loss}
        #debug_log.warn("solutions for generation {}: {}".format(gen, solutions))
        sampler.tell(solutions)

    return gens_summary
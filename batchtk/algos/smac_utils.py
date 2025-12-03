from ConfigSpace import Configuration, ConfigurationSpace, Float, Integer, Categorical
from typing import Optional
import numpy, pandas
import uuid
from smac import HyperparameterOptimizationFacade, Scenario
from batchtk import runtk
from batchtk.utils import SQLStorage, SQLiteStorage, create_logger, expand_path
from batchtk.runtk.trial import trial as runtk_trial
from batchtk.runtk.trial import LABEL_POINTER, DIR_POINTER
from logging import Logger
import warnings
from batchtk.utils.version import deprecated_arg, create_deprecation_handlers
from batchtk.runtk import constructors

_SPACE_SAMPLERS = { # samplers for
    'categorical': Categorical,
    'int': Integer,
    'float': Float}

#_SAMPLERS = {
#    'hpo': HyperparameterOptimizationFacade,
#}



@deprecated_arg({"output_path": "output_dir", "project_path": "project_dir"}, deprecated_since="0.1.7", removal_when="0.1.9")
def smac_search(
    #algo args
    study_label: str = None, param_space: dict | ConfigurationSpace = None, metrics: dict = None,
    param_space_samplers: list | bool = None, num_trials: int = 0, num_workers: int = 1,
    algo: Optional[str] = None, algo_kwargs: Optional[dict] = None,
    seed: Optional[int] = None,
    #trial args
    dispatcher_constructor: callable = None, project_dir: str = None,
    output_dir: str = None, submit_constructor: callable = None,
    checkpoint_dir: str = None, dispatcher_kwargs: Optional[dict] = None,
    submit_kwargs: Optional[dict] = None, interval: Optional[int] = 60,
    storage_constructor: Optional[callable] = constructors.SQLiteStorage,
    log_constructor: Optional[callable] = constructors.BatchtkLogger,
    log_kwargs: Optional[dict] = None, report: Optional[list] = ('path', 'config', 'data'),
    cleanup: Optional[bool | list | tuple] = (runtk.SGLOUT, runtk.MSGOUT),
    check_storage: Optional[bool] = True, ** kwargs) -> (HyperparameterOptimizationFacade, Configuration):

    checkpoint_dir = checkpoint_dir or output_dir
    # set up debug_log first...
    log_kwargs = log_kwargs or {'file_out': f"{checkpoint_dir}/{study_label}.log"}
    if log_constructor:
        try:
            debug_log = log_constructor(**log_kwargs)
            assert isinstance(debug_log, Logger)
        except Exception as e:
            raise ValueError(
                f"log_constructor {log_constructor} must return an instance of class Logger when called with **log_kwargs {log_kwargs}, instead encountered error: {e}.")
    else:
        raise ValueError(f"log_constructor must be provided for cmaes_search to set up debug_log.")

    # generate the storage kwargs:
    storage_kwargs = {
        'directory': checkpoint_dir,
        'label': study_label
    }

    #if num_workers > 1:
    #    warnings.warn('smac_search implementation currently only supports single process search.')
    #    num_workers = 1
    configuration_space = None
    if isinstance(param_space, ConfigurationSpace):
        configuration_space = param_space
        param_space_samplers = True # already have a properly supplied configuration space
    if param_space_samplers is None:
        param_space_samplers = [Float] * len(param_space)
    else:
        if len(param_space_samplers) != len(param_space):
            raise ValueError("param_space_samplers must have corresponding ('categorical', 'int', 'float') strings for each param_space")
        if not all(sampler in ('categorical', 'int', 'float') for sampler in param_space_samplers):
            raise ValueError("all param_space_samplers must be one of 'categorical', 'int', or 'float'")
        param_space_samplers = [ _SPACE_SAMPLERS[sampler] for sampler in param_space_samplers ]
    if configuration_space is None:
        configuration_space = ConfigurationSpace(
            space= {key: param_space_samplers[i](name=key, bounds=args) for i, (key, args) in enumerate(param_space.items())}
        )

    keys, directions = zip(*metrics.items())
    directions = [1 if direction == 'minimize' else -1 for direction in directions]

    def eval_trial(cfg, seed):
        config_dict = cfg.get_dictionary() # cfg is a configspace.Configuration, not a dictionary...
        tid = str(uuid.uuid4())  # SMAC3 smac doesn't provide a way to handle ID.
        config_dict['_batchtk_label_pointer'] = LABEL_POINTER
        config_dict['_batchtk_path_pointer'] = DIR_POINTER
        data = runtk_trial(
            config=config_dict,
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
            storage_kwargs=storage_kwargs,
            log_constructor=log_constructor,
            log_kwargs=log_kwargs,
            report=report,
            cleanup=cleanup,
            check_storage=check_storage
        )
        loss = [float(data[key]) * direction for key, direction in zip(keys, directions)]
        return loss


    scenario_kwargs = {  # default, internal values for now...
        "deterministic": True,
        "objectives": keys,
        "n_trials": num_trials,
        "seed": seed or -1,
        "n_workers": num_workers,
    }

    scenario = Scenario(configuration_space, **scenario_kwargs)
    algo_kwargs = {
        "objective_weights": None,
    }
    #File
    #"batchtk/batchtk/algos/smac_utils.py", line
    #134, in smac_search
    #smac = HyperparameterOptimizationFacade(**facade_kwargs)
    #^^^

    facade_kwargs = {
        "scenario": scenario,
        "target_function": eval_trial,
        "multi_objective_algorithm": HyperparameterOptimizationFacade.get_multi_objective_algorithm(
            scenario, **algo_kwargs,
        ),
        "overwrite": False,
    }

    smac = HyperparameterOptimizationFacade(**facade_kwargs)

    incumbents = smac.optimize()

    data_storage = storage_constructor(**storage_kwargs)
    df = data_storage.to_df()
    #TODO look into returning smac as well?
    return df
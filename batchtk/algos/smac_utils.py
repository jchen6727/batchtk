from ConfigSpace import Configuration, ConfigurationSpace, Float, Integer, Categorical
from typing import Optional
import numpy, pandas
from smac import HyperparameterOptimizationFacade, Scenario
from batchtk import runtk
from batchtk.utils import SQLStorage, ScriptLogger, expand_path
from batchtk.runtk.trial import trial as runtk_trial
from batchtk.runtk.trial import LABEL_POINTER
from logging import Logger
import warnings

_SPACE_SAMPLERS = { # samplers for
    'categorical': Categorical,
    'int': Integer,
    'float': Float}

#_SAMPLERS = {
#    'hpo': HyperparameterOptimizationFacade,
#}


def smac_search(study_label: str = None, param_space: dict | ConfigurationSpace = None, metrics: dict = None,
           param_space_samplers: list | bool = None, num_trials: int = 0, num_workers: int = 1,
           dispatcher_constructor: callable = None, project_path: str = None,
           output_path: str = None, submit_constructor: callable = None,
           algo: Optional[str] = None, algo_kwargs: Optional[dict] = None,
           seed: Optional[int] = None,
           dispatcher_kwargs: Optional[dict] = None,
           submit_kwargs: Optional[dict] = None, interval: Optional[int] = 60,
           data_storage: Optional[SQLStorage] = None,
           debug_log: Optional[Logger | str] = None,
           report: Optional[list] = ('path', 'config', 'data'),
           cleanup: Optional[bool | list | tuple] = (runtk.SGLOUT, runtk.MSGOUT),
           check_storage: Optional[bool] = True
) -> (HyperparameterOptimizationFacade, Configuration):
    if num_workers > 1:
        warnings.warn('smac_search implementation currently only supports single process search.')
        num_workers = 1
    if isinstance(debug_log, str):
        debug_log = ScriptLogger(debug_log)
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
    debug_log = debug_log or ScriptLogger()
    data_storage = data_storage or SQLStorage(directory=output_path, filename='smac3.sqlite.db')
    if not isinstance(data_storage, SQLStorage):
        raise ValueError("data_storage must be a SQLStorage instance")
    keys, directions = zip(*metrics.items())
    directions = [1 if direction == 'minimize' else -1 for direction in directions]
    def eval_trial(cfg: Configuration, seed: int = None):
        #cfg = {key: trial.getattr(param_space_samplers[i])(key, *args) for i, (key, args) in enumerate(param_space.items())}
        tid = "{}".format(cfg.config_id)
        data = runtk_trial(
            config=cfg,
            label=study_label,
            tid=tid,
            dispatcher_constructor=dispatcher_constructor,
            project_path=project_path,
            output_path=output_path,
            submit_constructor=submit_constructor,
            dispatcher_kwargs=dispatcher_kwargs,
            submit_kwargs=submit_kwargs,
            interval=interval,
            data_storage=data_storage,
            debug_log=debug_log,
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

    df = data_storage.to_df()
    #return smac
    return df
from ConfigSpace import Configuration, ConfigurationSpace, Float, Integer, Categorical
from typing import Optional
import numpy, pandas
from smac import HyperparameterOptimizationFacade, Scenario
from batchtk import runtk
from batchtk.utils import SQLStorage, ScriptLogger, expand_path
from batchtk.runtk.trial import trial as runtk_trial
from logging import Logger


def smac_search(study_label: str = None, param_space: dict | ConfigurationSpace = None, metrics: dict = None,
           param_space_samplers = None, num_trials: int = 0, num_workers: int = 1,
           dispatcher_constructor: callable = None, project_path: str = None,
           output_path: str = None, submit_constructor: callable = None,
           algo: Optional[str] = None, algo_kwargs: Optional[dict] = None,
           seed: Optional[int] = None,
           dispatcher_kwargs: Optional[dict] = None,
           submit_kwargs: Optional[dict] = None, interval: Optional[int] = 60,
           data_storage: Optional[SQLStorage] = None, optuna_storage: Optional = None,
           debug_log: Optional[Logger | str] = None,
           report: Optional[list] = ('path', 'config', 'data'),
           cleanup: Optional[bool | list | tuple] = (runtk.SGLOUT, runtk.MSGOUT),
           check_storage: Optional[bool] = True
) -> pandas.DataFrame:
    if isinstance(debug_log, str):
        debug_log = ScriptLogger(debug_log)
    configuration_space = None
    if isinstance(param_space, ConfigurationSpace):
        configuration_space = param_space
        param_space_samplers = True # already have the samplers with ConfigurationSpace--
    if param_space_samplers is None:
        param_space_samplers = [Float] * len(param_space)
    else:
        if len(param_space_samplers) != len(param_space):
            raise ValueError("param_space_samplers must have corresponding ('categorical', 'int', 'float') strings for each param_space")
        if not all(sampler in ('categorical', 'int', 'float') for sampler in param_space_samplers):
            raise ValueError("all param_space_samplers must be one of 'categorical', 'int', or 'float'")
        param_space_samplers = [ 'suggest_' + sampler for sampler in param_space_samplers]
    debug_log = debug_log or ScriptLogger()
    keys, directions = zip(*metrics.items())
    def eval_trial(trial):
        cfg = {key: trial.getattr(param_space_samplers[i])(key, *args) for i, (key, args) in enumerate(param_space.items())}
        tid = "{}".format(trial.number)
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
        loss = [float(data[key]) for key in keys]
        return loss
    algo_kwargs = algo_kwargs or {}
    if seed:
        algo_kwargs['seed'] = seed
    sampler = _SAMPLERS[algo](**algo_kwargs) if algo in _SAMPLERS else None # if algo is provided...
    algo = algo or 'optuna' # change algo to optuna for labeling.
    study_name = "".join(('_' + _str for _str in (algo, seed) if _str)) # fix later.
    study_name = "{}{}".format(study_label, study_name)
    if optuna_storage is None:
        optuna_storage = JournalStorage(JournalFileStorage("{}/{}.optuna.journal.log".format(output_path, study_name)))
    study = optuna.create_study(directions=directions,
                                storage=optuna_storage,
                                load_if_exists=True,
                                sampler=sampler,
                                study_name='{}'.format(study_name))
    study.optimize(eval_trial, n_trials=num_trials, n_jobs=num_workers)

    return study.trials_dataframe()

configspace = ConfigurationSpace({"C": (0.100, 1000.0)})

# Scenario object specifying the optimization environment
scenario = Scenario(configspace, deterministic=True, n_trials=200)

# Use SMAC to find the best configuration/hyperparameters
smac = HyperparameterOptimizationFacade(scenario, train)
incumbent = smac.optimize()
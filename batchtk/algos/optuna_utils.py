import optuna
import pandas
from typing import Optional
from batchtk import runtk
from batchtk.utils import SQLStorage, ScriptLogger, expand_path
from batchtk.runtk.trial import trial as runtk_trial
from logging import Logger
from optuna.storages import JournalStorage, JournalFileStorage

_SAMPLERS = {
    'nsgaii': optuna.samplers.NSGAIISampler,
    'random': optuna.samplers.RandomSampler,
    'tspe':  optuna.samplers.TPESampler,
}

def optuna_search(study_label: str = None, param_space: dict = None, metrics: dict = None,
           num_trials: int = 0, num_workers: int = 1,
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
    """
    Perform an optimization search using Optuna.
    study_label: str - label for the study (used in storage and logging)
    param_space: dict - dictionary defining the parameter search space, keys are parameter names and values are tuples defining (lower_bound, upper_bound)
    metrics: dict - dictionary defining the metrics to optimize, keys are metric names and values are 'minimize' or 'maximize'
    num_trials: int - number of trials to run
    num_workers: int - number of parallel workers to
    """
    if isinstance(debug_log, str):
        debug_log = ScriptLogger(debug_log)

    debug_log = debug_log or ScriptLogger()
    keys, directions = zip(*metrics.items())
    def eval_trial(trial):
        cfg = {key: trial.suggest_float(key, *bounds) for key, bounds in param_space.items()}
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

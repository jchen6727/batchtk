import cmaes

from batchtk import runtk
from batchtk.utils import SQLStorage, ScriptLogger, expand_path
from batchtk.runtk.trial import trial as runtk_trial
import pandas
from typing import Optional
from batchtk import runtk

from batchtk.runtk.trial import trial as runtk_trial

from batchtk.runtk.trial import LABEL_POINTER, PATH_POINTER

from logging import Logger

_SAMPLERS = { # refer #https://github.com/CyberAgentAILab/cmaes/tree/main
    'base': cmaes.CMA,
    'margin': cmaes.CatCMAwM,
}
def cmaes_search(
    study_label: str = None, param_space: dict = None, metrics: dict = None,
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
    """
    Perform an optimization search using CMAES.
    study_label: str - label for the study (used in storage and logging)
    param_space: dict - dictionary defining the parameter search space, keys are parameter names and values are tuples defining (lower_bound, upper_bound)
    metrics: dict - dictionary defining the metrics to optimize and the direction of optimization, keys are metric names and values are 'minimize' (search for lowest value) or 'maximize' (search for highest value)
    param_space_samplers: list - list of strings defining the sampler for each parameter in param_space, one of 'categorical', 'int', or 'float' (defaults to 'float' for all parameters)
    num_trials: int - number of trials to run
    num_workers: int - number of trials to be run in parallel (uses multiprocessing)
    dispatcher_constructor: callable - calling function to a dispatcher class -- see dispatchers.py
    project_path: str - path to the project directory containing the source code to be executed
    output_path: str - path to the output directory where runtime files, results and logs will be stored
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
    if isinstance(debug_log, str):
        debug_log = ScriptLogger(debug_log)
    debug_log = debug_log or ScriptLogger()

    algo_kwargs = algo_kwargs or {}
    if not all(sampler in ('categorical', 'int', 'float') for sampler in param_space_samplers):
        raise ValueError("all param_space_samplers must be one of 'categorical', 'int', or 'float'")
    if any(sampler in ('categorical', 'int') for sampler in param_space_samplers):
        debug_log.warn("Categorical and Integer sampling in param_space, using margin sampler.")
        algo = 'margin'
        param_x = []
        param_c = []
        param_z = []
        for key in ('x_space', 'z_space', 'c_space'):
            if key not in algo_kwargs:
                algo_kwargs[key] = []
        for i, (key, args) in enumerate(param_space.items()):
            if param_space_samplers[i] == 'float':
                param_x.append(key)
                algo_kwargs['x_space'].append([args[0], args[1]])
            if param_space_samplers[i] == 'int':
                param_z.append(key)
                algo_kwargs['z_space'].append([args[0], args[1]])
            if param_space_samplers[i] == 'categorical':
                param_c.append(key)
                algo_kwargs['c_space'].append(len(args))

    keys, directions = zip(*metrics.items())
    def eval_trial(trial):
        cfg = {key: trial.__getattribute__(param_space_samplers[i])(key, *args) for i, (key, args) in enumerate(param_space.items())}
        tid = "{}".format(trial.number)
        cfg['_batchtk_label_pointer'] = LABEL_POINTER
        cfg['_batchtk_path_pointer'] = PATH_POINTER
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


from batchtk.runtk import LocalDispatcher, SHSubmitSFS
from batchtk.utils import SQLiteLogger
from batchtk.runtk.trial import trial
from header import LEN

from batchtk.runtk.trial import trial, LABEL_POINTER, PATH_POINTER

from cmaes import CMA # CMA_ES
# see https://github.com/CyberAgentAILab/cmaes/tree/main
import numpy
import os

NUM_GEN = 3

path = os.getcwd()

entries = ["fx", *["x.{}".format(i) for i in range(LEN)]]
log = SQLiteLogger(path='../rosenbrock_out', entries=entries)
# evaluation
def eval_rosenbrock(x, tid):
    cfg = { 'x.{}'.format(i): x[i] for i in range(len(x)) }
    data = trial(
        config=cfg,
        label='rosenbrock',
        tid=tid,
        dispatcher_constructor=LocalDispatcher,
        project_path=path,
        output_path='../rosenbrock_out',
        submit_constructor=SHSubmitSFS,
        dispatcher_kwargs=None,
        submit_kwargs={'command': 'python rosenbrock.py'},
        interval=1,
        log=log,
        report=('path', 'data')
    )
    return float(data['fx'])




# suggestor
optimizer = CMA(mean=numpy.zeros(LEN), sigma=1.0)
for generation in range(NUM_GEN):
    solutions = []
    for cand in range(optimizer.population_size):
        x = optimizer.ask()
        value = eval_rosenbrock(x, "{}_{}".format(generation, cand))
        solutions.append((x, value))
        print(f"#{generation} fx={value} (x={x})")
    optimizer.tell(solutions)

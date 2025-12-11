import importlib
from typing import Tuple, Type

from pymoo.core.algorithm import Algorithm
from pymoo.parallelization.starmap import StarmapParallelization
from pymoo.optimize import minimize
from pymoo.core.problem import Problem, ElementwiseProblem
from pymoo.termination import get_termination
from pymoo.termination.collection import TerminationCollection

import pandas
from typing import Optional
from batchtk import runtk
from batchtk.utils import SQLStorage, create_logger, expand_path
from batchtk.runtk.trial import trial, LABEL_POINTER, DIR_POINTER
from batchtk.runtk import constructors
from batchtk.runtk.trial import trial, LABEL_POINTER, DIR_POINTER
from batchtk.utils.version import deprecated_arg, create_deprecation_handlers
from batchtk.algos import Trial
from logging import Logger

from pymoo.optimize import minimize

from pymoo.core.problem import ElementwiseProblem

import numpy

from batchtk.utils import expand_path

# see https://pymoo.org/algorithms/list.html#nb-algorithms-list
def _get_algo(path: Tuple[str, ...]) -> Type[Algorithm]:
    """
    Factory function to dynamically import and return a pymoo algorithm class.

    Args:
        path: A tuple representing the traversal path from `pymoo.algorithms`.
                For example: `('soo', 'nonconvex', 'pso', 'PSO')` corresponds to
                `from pymoo.algorithms.soo.nonconvex.pso import PSO`.

    Returns:
        The algorithm class.

    Raises:
        ImportError: If the module path is invalid.
        AttributeError: If the algorithm is not found in the specified module.
    """
    if not path:
        raise ValueError("Path cannot be empty.")
    module_path_parts = path[:-1]
    class_name = path[-1]
    # Construct the full, dot-separated module path
    full_module_path = f"pymoo.algorithms.{'.'.join(module_path_parts)}"
    # Dynamically import the module
    module = importlib.import_module(full_module_path)
    # Get the algorithm class from the module
    algorithm_class = getattr(module, class_name)
    return algorithm_class

_SAMPLERS = {
    'GA': ('soo', 'nonconvex', 'ga', 'GA'),
    'DE': ('soo', 'nonconvex', 'de', 'DE'),
    'BRKGA': ('soo', 'nonconvex', 'brkga', 'BRKGA'),
    'NelderMead': ('soo', 'nonconvex', 'nelder', 'NelderMead'),
    'PatternSearch': ('soo', 'nonconvex', 'pattern', 'PatternSearch'),
    'CMAES': ('soo', 'nonconvex', 'cmaes', 'CMAES'),
    'ES': ('soo', 'nonconvex', 'es', 'ES'),
    'SRES': ('soo', 'nonconvex', 'sres', 'SRES'),
    'ISRES': ('soo', 'nonconvex', 'isres', 'ISRES'),
    'PSO': ('soo', 'nonconvex', 'pso', 'PSO'),
    'NRBO': ('soo', 'nonconvex', 'nrbo', 'NRBO'),
    'NSGA2': ('moo', 'nsga2', 'NSGA2'),
    'RNSGA2': ('moo', 'rnsga2', 'RNSGA2'),
    'NSGA3': ('moo', 'nsga3', 'NSGA3'),
    'UNSGA3': ('moo', 'unsga3', 'UNSGA3'),
    'RNSGA3': ('moo', 'rnsga3', 'RNSGA3'),
    'MOEAD': ('moo', 'moead', 'MOEAD'),
    'CTAEA': ('moo', 'ctaea', 'CTAEA'),
    'RVEA': ('moo', 'rvea', 'RVEA'),
    'SPEA2': ('moo', 'spea2', 'SPEA2'),
}

class TrialProblem(ElementwiseProblem, Trial):
    def __init__(self, label: str, params: dict[str, tuple[float, float]],
                 metrics: dict, n_ieq_constr = 0, n_eq_constr = 0,
                 dispatcher_constructor = None, project_dir = None,
                 output_dir = None, submit_constructor = None,
                 storage_dir = None, dispatcher_kwargs = None,
                 submit_kwargs = None, interval = 60,
                 storage_constructor = constructors.SQLiteStorage,
                 storage_kwargs = None,
                 log_constructor = constructors.BatchtkLogger,
                 log_kwargs = None, report = ('path', 'config', 'data'),
                 cleanup = (runtk.SGLOUT, runtk.MSGOUT),
                 check_storage = True, **kwargs
                 ):
        n_var = len(params)
        n_obj = len(metrics)
        self.metrics = sorted(metrics)
        self.params, xb = zip(*params.items())
        xl, xu = zip(*xb)
        super().__init__(n_var=n_var, n_obj=n_obj, n_ieq_constr=n_ieq_constr,
                         n_eq_constr=n_eq_constr, xl=xl, xu=xu, **kwargs)
        self._fixed_trial_args = dict()
        self.set_fixed_trial_args(
            dispatcher_constructor=dispatcher_constructor, project_dir=project_dir,
            output_dir=output_dir, submit_constructor=submit_constructor,
            storage_dir=storage_dir, dispatcher_kwargs=dispatcher_kwargs,
            submit_kwargs=submit_kwargs, interval=interval,
            storage_constructor=storage_constructor, storage_kwargs=storage_kwargs,
            log_constructor=log_constructor, log_kwargs=log_kwargs, report=report,
            cleanup=cleanup, check_storage=check_storage,
        )
        self.label = label
    def _evaluate(self, x, out, *args, **kwargs):
        config = {param: x for param, x in zip(self.params, x)}
        tid = self.compute_id_from_args(self.label, config)
        results = self.run_trial(
            config=config,
            label=self.label,
            tid=tid
        )
        out["F"] = [results[metric] for metric in self.metrics]

termination = TerminationCollection(
    get_termination("n_gen", 3),
)

dispatcher_constructor = constructors.LocalDispatcher
project_dir = expand_path('../runner_scripts', create_dirs=True)
output_dir = expand_path('./output', create_dirs=True)
submit_constructor = constructors.SHSubmit
storage_dir = expand_path('./output', create_dirs=True)
submit_kwargs = {'command': 'python rosenbrock.py'}
storage_constructor = constructors.SQLiteStorage
log_constructor = constructors.BatchtkLogger

workers = 5
if __name__ == '__main__':
    pool = multiprocessing.Pool(workers)
    runner = StarmapParallelization(pool.starmap)
    problem = TrialProblem(
        label='rosenbrock',
        params={'x0': (-3, 3), 'x1': (-3, 3)},
        metrics={'fx': 'minimize'},
        dispatcher_constructor=dispatcher_constructor,
        project_dir=project_dir,
        output_dir=output_dir,
        submit_constructor=submit_constructor,
        storage_dir=storage_dir,
        submit_kwargs=submit_kwargs,
        storage_constructor=storage_constructor,
        log_constructor=log_constructor,
        elementwise_runner=runner,
    )


    algorithm = GA(
        pop_size=workers,
        eliminate_duplicates=True)

    res = minimize(problem,
                   algorithm,
                   termination,
                   seed=1,
                   verbose=False)

    print("Best solution found: \nX = %s\nF = %s" % (res.X, res.F))

@deprecated_arg({"output_path": "output_dir", "project_path": "project_dir"}, deprecated_since="0.1.7", removal_when="0.1.9")
def pymoo_search(
    # algo args
    study_label: str = None, param_space: dict = None, metrics: dict = None,
    param_space_samplers = None, num_trials: int = 0, num_workers: int = 1,
    algo: Optional[str] = None, algo_kwargs: Optional[dict] = None,
    seed: Optional[int] = None, optuna_storage: Optional = None,

    # trial args
    dispatcher_constructor: callable = None, project_dir: str = None,
    output_dir: str = None, submit_constructor: callable = None,
    storage_dir: str = None, dispatcher_kwargs: Optional[dict] = None,
    submit_kwargs: Optional[dict] = None, interval: Optional[int] = 60,
    storage_constructor: Optional[callable] = constructors.SQLiteStorage,
    storage_kwargs: Optional[dict] = None,
    log_constructor: Optional[callable] = constructors.BatchtkLogger,
    log_kwargs: Optional[dict] = None, report: Optional[list] = ('path', 'config', 'data'),
    cleanup: Optional[bool | list | tuple] = (runtk.SGLOUT, runtk.MSGOUT),
    check_storage: Optional[bool] = True, **kwargs) -> pandas.DataFrame:
    """
    Perform an optimization search using Optuna.
    study_label: str - label for the study (used in storage and logging)
    param_space: dict - dictionary defining the parameter search space, keys are parameter names and values are tuples defining (lower_bound, upper_bound)
    metrics: dict - dictionary defining the metrics to optimize and the direction of optimization, keys are metric names and values are 'minimize' (search for lowest value) or 'maximize' (search for highest value)
    param_space_samplers: list - list of strings defining the sampler for each parameter in param_space, one of 'categorical', 'int', or 'float' (defaults to 'float' for all parameters)
    num_trials: int - number of trials to run
    num_workers: int - number of trials to be run in parallel (uses multiprocessing)
    dispatcher_constructor: callable - calling function to a dispatcher class -- see dispatchers.py
    project_dir: str - path to the project directory containing the source code to be executed
    output_dir: str - path to the output directory where runtime files, results and logs will be stored
    storage_dir: str - optional additional path to the directory where checkpoints will be stored (otherwise defaults to output_dir)
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
    storage_dir = storage_dir or output_dir
    log_kwargs = log_kwargs or {'file_out': f"{storage_dir}/{study_label}.log"}
    if log_constructor:
        try:
            debug_log = log_constructor(**log_kwargs)
            assert isinstance(debug_log, Logger)
        except Exception as e:
            raise ValueError(
                f"log_constructor {log_constructor} must return an instance of class Logger when called with **log_kwargs {log_kwargs}, instead encountered error: {e}.")
    else:
        raise ValueError(f"log_constructor must be provided for cmaes_search to set up debug_log.")

    algo_kwargs = algo_kwargs or {'pop_size': num_workers, 'eliminate_duplicates': True}

    try:
        algo = _get_algo(_SAMPLERS[algo]) if algo else _get_algo(_SAMPLERS['NSGA3'])
    except KeyError:
        raise ValueError(f"algo must be one of {list(_SAMPLERS.keys())}") from None

    if param_space_samplers is not None:
        if len(param_space_samplers) != len(param_space):
            raise ValueError("param_space_samplers must have corresponding ('categorical', 'int', 'float') strings for each param_space")
        if not all(sampler in ('float') for sampler in param_space_samplers):
            raise ValueError("all param_space_samplers must be one of 'float'")

    search_kwargs = {
        
    }
    return minimize(TrialProblem(label=study_label, params=param_space, metrics=metrics),
                   algo,
                   **algo_kwargs)
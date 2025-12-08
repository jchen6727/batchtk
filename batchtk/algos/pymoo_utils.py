import importlib
from typing import Tuple, Type

from pymoo.core.algorithm import Algorithm

import pandas
from typing import Optional
from batchtk import runtk
from batchtk.utils import SQLStorage, create_logger, expand_path
from batchtk.runtk.trial import trial as runtk_trial

from batchtk.runtk import constructors
from batchtk.runtk.trial import LABEL_POINTER, DIR_POINTER
from batchtk.utils.version import deprecated_arg, create_deprecation_handlers

from logging import Logger

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

@deprecated_arg({"output_path": "output_dir", "project_path": "project_dir"}, deprecated_since="0.1.7", removal_when="0.1.9")
def optuna_search(
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

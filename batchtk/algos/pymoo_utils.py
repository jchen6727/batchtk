import importlib
from typing import Tuple, Type

from pymoo.core.algorithm import Algorithm
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.moo.moead import MOEAD
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.algorithms.moo.spea2 import SPEA2
# see https://pymoo.org/algorithms/list.html#nb-algorithms-list

def get_algorithm(name: str, **kwargs):
    """
    Factory function to get a pymoo algorithm instance.

    Args:
        name (str): The name of the algorithm (e.g., "GA", "NSGA2").
        **kwargs: Keyword arguments to pass to the algorithm constructor.

    Returns:
        An instance of the specified pymoo algorithm.

    Raises:
        ValueError: If an unknown algorithm name is provided.
    """
    algorithms = {
        "GA": GA,
        "NSGA2": NSGA2,
        "MOEAD": MOEAD,
        "NSGA3": NSGA3,
        "SPEA2": SPEA2,
    }

    algo_class = algorithms.get(name)
    if algo_class:
        return algo_class(**kwargs)
    else:
        raise ValueError(f"Unknown pymoo algorithm: {name}. "
                         f"Available algorithms: {', '.join(algorithms.keys())}")


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


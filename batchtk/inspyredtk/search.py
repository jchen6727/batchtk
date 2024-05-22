from inspyred import ec
import random
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from batchtk.utils import path_open, get_path
import logging
#per: https://aarongarrett.github.io/inspyred/troubleshooting.html
"""
my_seed = int(time.time())
seedfile = open('randomseed.txt', 'w')
seedfile.write('{0}'.format(my_seed))
seedfile.close()
prng = random.Random()
prng.seed(my_seed)

import logging
logger = logging.getLogger('inspyred.ec')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('inspyred.log', mode='w')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
"""

# each ALGO has custom kwargs
# see https://pythonhosted.org/inspyred/reference.html
ALGO = {
    'DEA': ec.DEA,
    'EDA': ec.EDA,
    'ES': ec.ES,
    'GA': ec.GA,
    'SA': ec.SA,
}

def ec_search(dispatcher_constructor: Callable,
              submit_constructor: Callable,
              run_config: Dict,
              params: Dict,
              algorithm: [str|Callable],
              algorithm_config: Optional[Dict] = None,
              label: Optional[str] = "search",
              output_path: Optional[str] = "../batch",
              generations: Optional[int] = 1,
              pop_size: Optional[int] = 1,
              seed: Optional[int] = None,
              logger: Optional[bool|logging.Logger] = None,
              **kwargs):
    """
    :param algorithm: string, algorithm name
    :param problem: function, problem function
    :param bounds: list, list of tuples of lower and upper bounds
    :param generations: int, number of generations
    :param pop_size: int, population size
    :param seed: int, random seed
    :param kwargs: dict, keyword arguments
    :return: list, list of best individuals
    """
    storage_path = get_path(output_path)

    if seed is None:
        seed = int(time.time())

    if logger is None:
        logger = logging.getLogger('inspyred.ec')
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler('{}/{}_ec.log'.format(storage_path), mode='a')
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    param_kwargs = {'params': [], 'lower_bounds': [], 'upper_bounds': [],}
    for param, bounds in params.items(): #restructure input parameters.
        param_kwargs['params'].append(param)
        param_kwargs['lower_bounds'].append(bounds[0])
        param_kwargs['upper_bounds'].append(bounds[1])

    file_kwargs = {
        'statistics_file': path_open(path = "{}/{}_ec_stats.csv".format(label, storage_path), mode='w'),
        'individuals_file': path_open(path = "{}/{}_ec_ind_stats.csv".format(label, storage_path), mode='w'),
    }

    with path_open(path = "{}/{}_ec.seed".format(label, storage_path), mode='w') as fptr:
        fptr.write(str(seed))

    random.seed(seed)
    prng = random.Random()
    prng.seed(seed)

    ea = ALGO[algorithm](prng)
    ea.terminator = ec.terminators.generation_termination
    ea.observer = [ec.observers.stats_observer, ec.observers.file_observer]
    ea.selector = ec.selectors.tournament_selection
    ea.variator = [ec.variators.uniform_crossover, ec.variators.gaussian_mutation]
    final_pop = ea.evolve(generator=ec.ec.generators.float_random, problem=problem, bounder=ec.ec.bounders.bounds, maximize=False, max_generations=generations, pop_size=pop_size, seed=seed, **kwargs)
    return final_pop


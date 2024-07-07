from inspyred import ec
import os
import random
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from batchtk.utils import path_open, get_path
from batchtk.runtk import trials, LABEL_POINTER
import logging

# each ALGO has custom kwargs
# see https://pythonhosted.org/inspyred/reference.html
ALGOS = {
    'DEA': ec.DEA, #differential evolutionary algorithm: {num_selected, tournament_size, crossover_rate, mutation_rate, gaussian_mean, gaussian_stdev}
    'EDA': ec.EDA, #estimation of distribution algorithm: {num_selected, num_offspring, num_elites}
    'ES': ec.ES, #evolution strategy: {tau, tau_prime, epsilon}
    'GA': ec.GA, #genetic algorithm: {num_selected, crossover_rate, num_crossover_points, mutation_rate, num_elites}
    'SA': ec.SA, #simulated annealing: {temperature, cooling_rate, mutation_rate, gaussian_mean, gaussian_stdev}
}

def generator(random, args):
    return [random.uniform(l, u) for l, u in zip(args.get('lower_bound'), args.get('upper_bound'))]


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

    prng = random.Random()
    if algorithm_config is None:
        algorithm_config = {}
    algorithm_config['pop_size'] = pop_size

    if seed is None:
        seed = int(time.time())

    prng.seed(seed)
    # per: https://aarongarrett.github.io/inspyred/troubleshooting.html
    with path_open(path="{}/{}_ec.seed".format(label, storage_path), mode='w') as fptr:
        fptr.write(str(seed))


    if algorithm in ALGOS:
        ea = ALGOS[algorithm](prng)
        # default termination
        # https://pythonhosted.org/inspyred/reference.html#inspyred.ec.terminators.generation_termination
        ea.terminator = ec.terminators.generation_termination
        terminator_kwargs = {'num_generations': generations}
    else:
        ea = algorithm
        # if the user supplies the ea, they will generate the terminator.
        terminator_kwargs = {}

    # see: https://pythonhosted.org/inspyred/reference.html#inspyred.ec.observers.file_observer
    # Optional keyword arguments in args:
    # statistics_file – a file object (default: see text)
    # individuals_file – a file object (default: see text)
    ea.observer = [ec.observers.stats_observer, ec.observers.file_observer]

    # per: https://aarongarrett.github.io/inspyred/troubleshooting.html
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

    observer_kwargs = {
        'statistics_file': path_open(path = "{}/{}_ec_stats.csv".format(label, storage_path), mode='w'),
        'individuals_file': path_open(path = "{}/{}_ec_ind_stats.csv".format(label, storage_path), mode='w'),
    }

    # kwarg resolution order:
    # algorithm_config -> param_kwargs -> observer_kwargs -> kwargs
    ea_kwargs = algorithm_config
    for _kwargs in [observer_kwargs, param_kwargs, terminator_kwargs, kwargs]:
        ea_kwargs.update(_kwargs)

    ea.observer = [ec.observers.stats_observer, ec.observers.file_observer]

    global gen
    gen = -1

    submit = submit_constructor()
    submit.update_templates(
        **run_config
    )
    project_path = os.getcwd()
    def eval_func(candidates, args):
        candidates['output_path'] = LABEL_POINTER
        gen += 1
        results = trials(configs = candidates,
                         label = label,
                         gen = gen,
                         dispatcher_constructor = dispatcher_constructor,
                         project_path = project_path,
                         output_path = output_path,
                         submit = submit,
               )
        return results

    final_pop = ea.evolve(
        generator      = generator,
        evaluator      = eval_func,
        bounder        = ec.ec.bounders.bounds,
        max_generations= generations,
        op_size        = pop_size,
        seed           = seed,
        **ea_kwargs)

    return final_pop


from batchtk.algos import optuna_search
from batchtk.utils import expand_path
from batchtk.runtk import LocalDispatcher
from batchtk.runtk import SHSubmitSFS
print(expand_path('./optimization', create_dirs=True))

search_space = {
    'x0': [-3, -2, -1],
    'x1': [1, 2, 3],
}

param_bounds = {
    key: [min(values), max(values)] for key, values in search_space.items()
}

param_space_samplers = ['float' for _ in search_space]

results = optuna_search(
    study_label='rosenbrock',
    param_space=param_bounds,
    param_space_samplers=param_space_samplers,  # specify integer sampling for both parameters
    metrics={'fx': 'minimize'},
    algo='grid',
    algo_kwargs={
        'search_space': search_space},  # 5 points for each parameter
    num_trials=9, num_workers=4,
    dispatcher_constructor=LocalDispatcher,
    submit_constructor=SHSubmitSFS,
    submit_kwargs={'command': 'python ../functions/rosenbrock_func.py'}, # normal run
    interval=10,
    project_path='.',
    output_path=expand_path('./optimization', create_dirs=True),
)

# manipulate results as needed

results = results.sort_values(by=['params_x0', 'params_x1'])[['params_x0', 'params_x1', 'value', 'number']]

# sort by x0, x1, then the trial result, then the id of the trial (to find the correct file)
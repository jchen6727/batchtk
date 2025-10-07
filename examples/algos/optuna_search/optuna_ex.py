from batchtk.algos import optuna_search
from batchtk.utils import expand_path
from batchtk.runtk import LocalDispatcher
from batchtk.runtk import SHSubmitSFS

results = optuna_search(
    study_label='rosenbrock',
    param_space={'x0': (-5, 5), 'x1': (-5, 5)},
    param_space_samplers=['int', 'int'],  # specify integer sampling for both parameters
    metrics={'fx': 'minimize'},
    num_trials=12, num_workers=3,
    dispatcher_constructor=LocalDispatcher,
    submit_constructor=SHSubmitSFS,
    submit_kwargs={'command': 'python ../functions/rosenbrock_func.py'}, # normal run
    interval=10,
    project_path='.',
    output_path=expand_path('./optimization', create_dirs=True),
)

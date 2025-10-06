from batchtk.algos import optuna_search
from batchtk.utils import expand_path

#option for local run
# dispatcher, submit = generate_constructors('sh', 'sfs')

#option for slurm run
dispatcher, submit = generate_constructors('slurm', 'sfs')

results = optuna_search(
    study_label='rosenbrock',
    param_space={'x0': (-5, 5), 'x1': (-5, 5)},
    param_space_samplers=['int', 'int'],  # specify integer sampling for both parameters
    metrics={'fx': 'minimize'},
    num_trials=12, num_workers=3,
    dispatcher_constructor=dispatcher,
    submit_constructor=submit,
    #submit_kwargs={'command': 'python single_opt.py'}, # normal run
    submit_kwargs=slurm_args,
    interval=10,
    project_path='.',
    output_path=expand_path('./optimization', create_dirs=True),
)

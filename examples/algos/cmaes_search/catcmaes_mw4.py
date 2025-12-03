from batchtk.algos import cmaes_search
from batchtk.utils import expand_path
from batchtk.runtk import LocalDispatcher
from batchtk.runtk import SHSubmitSFS

DEFAULT_NUMVAR = 4 # flexible number of variables ...
DEFAULT_NUMOBJ = 1 # flexible number of objectives ...

param_space = {'x{}'.format(i): (0.2, 0.4, 0.6, 0.8, 1.0) for i in range(DEFAULT_NUMVAR)}
metrics = {'F{}'.format(i): 'minimize' for i in range(DEFAULT_NUMOBJ)}
param_space_samplers = ['categorical' for _ in range(DEFAULT_NUMVAR)]  # specify float sampling for all parameters
results = cmaes_search(
    study_label='mw4',
    param_space=param_space,
    param_space_samplers=param_space_samplers,  # specify integer sampling for both parameters
    algo_kwargs={'seed': 42}, # for reproducibility
    metrics=metrics,
    num_trials=9, num_workers=3,
    dispatcher_constructor=LocalDispatcher,
    submit_constructor=SHSubmitSFS,
    submit_kwargs={'command': 'python ../functions/mw4.py'},  # normal run
    interval=3,
    project_dir='.',
    output_dir=expand_path('./optimization', create_dirs=True),
    checkpoint_dir=expand_path('./checkpoint_mw4', create_dirs=True),
)

with open('mw4_results.txt', 'w') as f:
    f.write(str(results))

print(results)

results = cmaes_search(
    study_label='rosenbrock',
    param_space={'x0': (-5, 5), 'x1': (-5, 5)},
    param_space_samplers=['int', 'int'],  # specify integer sampling for both parameters
    metrics={'fx': 'minimize'},
    num_trials=12, num_workers=3,
    dispatcher_constructor=Dispatcher,
    dispatcher_kwargs = {'connection_constructor': TOTPConnection,
                         'connection_kwargs': {'host': 'expanse0',
                                               'key': secret_key}},
    submit_constructor=Submit,
    submit_kwargs=slurm_args, # normal run
    interval=10,
    project_dir='/home/jchen12/dev/test_batchtk_netpyne/sim_scripts',
    output_dir='/home/jchen12/dev/test_batchtk_netpyne/output_cmaes',
    checkpoint_dir=expand_path('/Users/jchen/dev/test_batchtk_netpyne/checkpoint_cmaes', create_dirs=True),
)

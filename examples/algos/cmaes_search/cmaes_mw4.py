from batchtk.algos import cmaes_search
from batchtk.utils import expand_path
from batchtk.runtk import LocalDispatcher
from batchtk.runtk import SHSubmitSFS

DEFAULT_NUMVAR = 4 # flexible number of variables ...
DEFAULT_NUMOBJ = 1 # flexible number of objectives ...

param_space = {'x{}'.format(i): (0.0, 1.0) for i in range(DEFAULT_NUMVAR)}
metrics = {'F{}'.format(i): 'minimize' for i in range(DEFAULT_NUMOBJ)}
param_space_samplers = ['float' for _ in range(DEFAULT_NUMVAR)]  # specify float sampling for all parameters
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
    project_path='.',
    output_path=expand_path('./optimization', create_dirs=True),
)

with open('mw4_results.txt', 'w') as f:
    f.write(str(results))

print(results)
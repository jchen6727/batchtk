from batchtk.algos import pymoo_search
from batchtk.utils import expand_path
from batchtk.runtk import LocalDispatcher
from batchtk.runtk import SHSubmitSFS

if __name__ == '__main__':
    results = pymoo_search(
        study_label='rosenbrock',
        param_space={'x0': (-5, 5), 'x1': (-5, 5)},
        param_space_samplers=['float', 'float'],  # specify integer sampling for both parameters
        algo='AGEMOEA',
        metrics={'fx': 'minimize'},
        num_trials=12, num_workers=6,
        dispatcher_constructor=LocalDispatcher,
        submit_constructor=SHSubmitSFS,
        submit_kwargs={'command': 'python ../functions/rosenbrock_func.py'},  # normal run
        interval=10,
        project_dir='.',
        output_dir=expand_path('./optimization', create_dirs=True),
    )

    results.to_csv('./optimization/pymoo_results.csv')
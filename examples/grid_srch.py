import ray
import pandas
import os

import numpy
from ray import tune
from ray import air
from ray.air import session
from ray.tune.search.basic_variant import BasicVariantGenerator

from pubtk.runtk.dispatchers import SH_Dispatcher
from pubtk.runtk.submit import Submit

template = """\
#!/bin/bash
#$ -N job{label}
#$ -pe smp 5
#$ -l h_vmem=32G
#$ -o {cwd}/{label}.run
cd {cwd}
source ~/.bashrc
export OUTFILE="{label}.out"
export SGLFILE="{label}.sgl"
{env}
time mpiexec -np $NSLOTS -hosts $(hostname) nrniv -python -mpi init.py
"""

CONCURRENCY = 4
SAVESTR = 'grid.csv'

cwd = os.getcwd()

grid = {'cfg.AMPA': tune.grid_search([0.75, 1.25]),
        'cfg.GABA': tune.grid_search([0.75, 1.25]),
        'cfg.NMDA': tune.grid_search([0.75, 1.25]),
        }

ray.init(
    runtime_env={"working_dir": ".", # needed for import statements
                 "excludes": ["*.csv",
                              "*.run",
                              "*." 
                              "ray/",
                              "output/"]}, # limit the files copied
    # _temp_dir=os.getcwd() + '/ray/tmp', # keep logs in same folder (keeping resources in same folder as "working_dir")
    # OSError: AF_UNIX path length cannot exceed 107 bytes
)

TARGET = pandas.Series(
    {'PYR': 3.34,
     'BC': 19.7,
     'OLM': 3.47})

def sge_run(config):
    sge = Submit(submit_template = "qsub {cwd}/{label}.sh", script_template = template)
    dispatcher = SH_Dispatcher(cwd = cwd, env = {}, submit = sge)
    dispatcher.add_dict(value_type="FLOAT", dictionary = config)
    dispatcher.create_job(prefix='batch')
    session.report({'loss': 0})

algo = BasicVariantGenerator(max_concurrent=CONCURRENCY)

print("=====grid search=====")
print(grid)

tuner = tune.Tuner(
    #objective,
    sge_run,
    tune_config=tune.TuneConfig(
        search_alg=algo,
        num_samples=1, # grid search samples 1 for each param
        metric="loss"
    ),
    run_config=air.RunConfig(
        local_dir="./ray_ses",
        name="grid",
    ),
    param_space=grid,
)

results = tuner.fit()

resultsdf = results.get_dataframe()

resultsdf.to_csv(SAVESTR)


import ray
import pandas
import json
import os
import numpy
from ray import tune
from ray import air
from ray.air import session
from ray.tune.search.basic_variant import BasicVariantGenerator

from pubtk.runtk.dispatchers import SFS_Dispatcher
from pubtk.runtk.submit import Submit

import time

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

CONCURRENCY = 3
SAVESTR = 'grid.csv'

cwd = os.getcwd()

grid = {'cfg.AMPA': tune.grid_search([0.5, 1.00, 1.5]),
        'cfg.GABA': tune.grid_search([0.5, 1.00, 1.5]),
        'cfg.NMDA': tune.grid_search([0.5, 1.00, 1.5]),
        }

ray.init(
    runtime_env={"working_dir": ".", # needed for import statements
                 "excludes": [
                              "*.csv",
                              "*.out",
                              "*.run",
                              "*.sh",
                              "*.sgl",
                              ]}
)

TARGET = pandas.Series(
    {'PYR': 3.33875,
     'BC' : 19.725,
     'OLM': 3.47,}
)
def sge_run(config):
    sge = Submit(submit_template = "qsub {cwd}/{label}.sh", script_template = template)
    dispatcher = SFS_Dispatcher(cwd = cwd, env = {}, submit = sge)
    dispatcher.add_dict(value_type="FLOAT", dictionary = config)
    dispatcher.run()
    data = dispatcher.get_run()
    while not data:
        data = dispatcher.get_run()
        time.sleep(5)
    dispatcher.clean(args='sw')
    data = pandas.read_json(data, typ='series', dtype=float)
    loss = numpy.square( TARGET - data[ ['PYR', 'BC', 'OLM'] ] ).mean()
    session.report({'loss': loss, 'PYR': data['PYR'], 'BC': data['BC'], 'OLM': data['OLM']})

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
        local_dir="../ray_ses",
        name="grid",
    ),
    param_space=grid,
)

results = tuner.fit()

resultsdf = results.get_dataframe()

resultsdf.to_csv(SAVESTR)


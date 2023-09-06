import utils
import ray
import pandas
import shutil
import os

import numpy
from ray import tune
from ray import air
from ray.air import session
#from ray.tune.search.optuna import OptunaSearch
from ray.tune.search.basic_variant import BasicVariantGenerator

import argparse

## specify CLI to function
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--concurrency', default=1)
parser.add_argument('-d', '--div', nargs=3, type=float, default=[0.5, 1.5, 2])
parser.add_argument('-s', '--save', '-o', '--output', default="output/grid")
#parser.add_argument('-p', '--params', nargs='+', default=['PYR->BC_AMPA', 'PYR->OLM_AMPA', 'PYR->PYR_AMPA'])
parser.add_argument('-p', '--params', nargs='+', default=['Z'*80])
parser.add_argument('-g', '--greps', nargs='+', default=['Z'*80])

args, call= parser.parse_known_args()
args= dict(args._get_kwargs())

cwd = os.getcwd()
kwargs = {
    'mpiexec': shutil.which('mpiexec'), 'cores': 4, 'nrniv': shutil.which('nrniv'),
    'python': shutil.which('python'), 'script': cwd + '/runner.py'
}

initial_params = { # weights from cfg, AMPA, GABA, NMDA
    'PYR->BC_AMPA' : 0.36e-3, "BC->BC_GABA"  : 4.5e-3 , "PYR->BC_NMDA" : 1.38e-3 ,
    'PYR->OLM_AMPA': 0.36e-3, "BC->PYR_GABA" : 0.72e-3, "PYR->OLM_NMDA": 0.7e-3  ,
    'PYR->PYR_AMPA': 0.02e-3, "OLM->PYR_GABA": 72e-3  , "PYR->PYR_NMDA": 0.004e-3,
}

param_keys = {
    param
    for param in initial_params
    for grep in args['greps']
    if grep in param
}

param_keys.update(args['params'])


# singlecore command string
PY_CMDSTR = "{python} {script}".format(**kwargs)

# multicore command strings (mpiexec and shell)
MPI_CMDSTR = "{mpiexec} -n {cores} {nrniv} -python -mpi -nobanner -nogui {script}".format(**kwargs)
#SH_CMDSTR = "{mpiexec} -n $NSLOTS {nrniv} -python -mpi -nobanner -nogui {script}".format(**kwargs)
SH_CMDSTR = "time mpiexec -hosts $(hostname) -n $NSLOTS nrniv -python -mpi -nobanner -nogui runner.py".format(**kwargs)


CONCURRENCY = int(args['concurrency'])
#NTRIALS = int(args['trials'])
SAVESTR = "{}.csv".format(args['save'])

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

#ray.init(runtime_env={"py_modules": [os.getcwd()]})
TARGET = pandas.Series(
    {'PYR': 3.34,
     'BC': 19.7,
     'OLM': 3.47})

def objective(config):
    sdata = utils.run(config, MPI_CMDSTR)
    loss = utils.mse(sdata, TARGET)
    report = dict(sdata=sdata, PYR=sdata['PYR'], BC=sdata['BC'], OLM=sdata['OLM'], loss=loss)
    session.report(report)

def sge_objective(config):
    data = utils.sge_run(config=config, cwd=cwd, cmdstr=SH_CMDSTR, cores=5)
    sdata = pandas.read_json(data, typ='series', dtype=float)
    loss = utils.mse(sdata, TARGET)
    session.report(dict(loss=loss, PYR=sdata['PYR'], BC=sdata['BC'], OLM=sdata['OLM']))

algo = BasicVariantGenerator(max_concurrent=CONCURRENCY)

param_space = { # create parameter space
    "netParams.connParams.{}.weight".format(k): numpy.linspace(v*args['div'][0], v*args['div'][1], int(args['div'][2])) 
    for k, v in initial_params.items() if k in param_keys
}

"""
param_space = { # create parameter space
    "netParams.connParams.{}.weight".format(k): numpy.linspace(v*args['div'][0], v*args['div'][1], int(args['div'][2])) 
    for k, v in initial_params.items() if k in args['params']
}
"""
param_grid = {
    k: tune.grid_search(v) for k, v in param_space.items()
}

print("=====grid search=====")
print(param_space)

utils.write_pkl(param_space, "{}.pkl".format(args['save']))

tuner = tune.Tuner(
    #objective,
    sge_objective,
    tune_config=tune.TuneConfig(
        search_alg=algo,
        num_samples=1, # grid search samples 1 for each param
        metric="loss"
    ),
    run_config=air.RunConfig(
        local_dir="./ray_ses",
        name="grid",
    ),
    param_space=param_grid,
)

results = tuner.fit()

resultsdf = results.get_dataframe()

utils.write_csv(resultsdf, SAVESTR)

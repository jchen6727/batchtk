import utils
import ray
import pandas
import shutil
import os

from ray import tune
from ray import air
from ray.air import session
from ray.tune.search.optuna import OptunaSearch
from ray.tune.search import ConcurrencyLimiter


RESUME = False
SAVESTR = "output/optuna"
cwd = os.getcwd()
cmd_args = {
    'mpiexec': shutil.which('mpiexec'), 'cores': 4, 'nrniv': shutil.which('nrniv'),
    'python': shutil.which('python'), 'script': cwd + '/runner.py'
}

initial_params = { # weights from cfg, AMPA, GABA, NMDA
    'PYR->BC_AMPA' : 0.36e-3, "BC->BC_GABA"  : 4.5e-3 , "PYR->BC_NMDA" : 1.38e-3 ,
    'PYR->OLM_AMPA': 0.36e-3, "BC->PYR_GABA" : 0.72e-3, "PYR->OLM_NMDA": 0.7e-3  ,
    'PYR->PYR_AMPA': 0.02e-3, "OLM->PYR_GABA": 72e-3  , "PYR->PYR_NMDA": 0.004e-3,
}

tune_range = tune.quniform(
    1e-6, 
    100000e-6, 
    1e-6, 
)

search_space = { k : tune_range for k in initial_params }

# multicore command strings (mpiexec and shell)
MPI_CMDSTR = "{mpiexec} -n {cores} {nrniv} -python -mpi -nobanner -nogui {script}".format(**cmd_args)
SH_CMDSTR = "time mpiexec -hosts $(hostname) -n $NSLOTS nrniv -python -mpi -nobanner -nogui runner.py"

TARGET = pandas.Series(
    {'PYR': 3.34,
     'BC': 19.7,
     'OLM': 3.47})

NTRIALS = 10

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

def objective(config):
    sdata = utils.run(config, MPI_CMDSTR)
    loss = utils.mse(sdata, TARGET)
    report = dict(PYR=sdata['PYR'], BC=sdata['BC'], OLM=sdata['OLM'], loss=loss)
    session.report(report)

def sge_objective(config):
    data = utils.sge_run(config=config, cwd=cwd, cmdstr=SH_CMDSTR, cores=5)
    sdata = pandas.read_json(data, typ='series', dtype=float)
    loss = utils.mse(sdata, TARGET)
    session.report(dict(PYR=sdata['PYR'], BC=sdata['BC'], OLM=sdata['OLM'], loss=loss))

optuna_algo = ConcurrencyLimiter(searcher=OptunaSearch(), max_concurrent=1, batch= True)

print("=====optuna search=====")
print(search_space)

if RESUME:
    optuna_tuner = tune.Tuner.restore(
        path="{}/ray/ray_ses/optuna".format(cwd), # the path where the previous failed run is checkpointed
        param_space = search_space,
        restart_errored= True,
        resume_unfinished= True,
    )
else:
    optuna_tuner = tune.Tuner(
        sge_objective, #objective (on machine) sge_objective (on submit)
        tune_config=tune.TuneConfig(
            search_alg=optuna_algo,
            metric="loss",
            mode="min",
            num_samples=NTRIALS,
        ),
        run_config=air.RunConfig(
            local_dir="./ray_ses",
            name="optuna",
        ),
        param_space=search_space,
    )

results = optuna_tuner.fit()
resultsdf = results.get_dataframe()
utils.write_csv(resultsdf, SAVESTR)
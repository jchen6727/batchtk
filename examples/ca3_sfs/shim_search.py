import ray
import pandas
import json
import os
import numpy

from ray import tune
from ray import air
from ray.air import session

from ray.tune.search import create_searcher, ConcurrencyLimiter, SEARCH_ALG_IMPORT

from pubtk.runtk.dispatchers import SFSDispatcher
from pubtk.runtk.submit import SGESubmitSFS

import time
ALGORITHM = "cfo"

submit = SGESubmitSFS()

submit.update_template(
    command = "time mpiexec -np $NSLOTS -hosts $(hostname) nrniv -python -mpi init.py",
    cores = "5",
    vmem = "32G"
)

CONCURRENCY = 1

NTRIALS = 250

SAVESTR = "{}{}.csv".format(ALGORITHM, NTRIALS)

if ALGORITHM not in SEARCH_ALG_IMPORT.keys():
    print("script requires an algorithm from the following options: ")
    print(SEARCH_ALG_IMPORT.keys())
    raise KeyError

searcher = create_searcher(ALGORITHM)

cwd = os.getcwd()

tune_range = tune.quniform(
    1e-6,
    100000e-6,
    1e-6,
)

params = [
    'PYR->BC_AMPA' , 'PYR->OLM_AMPA', 'PYR->PYR_AMPA',
    'BC->BC_GABA'  , 'BC->PYR_GABA' , 'OLM->PYR_GABA',
    'PYR->BC_NMDA' , 'PYR->OLM_NMDA', 'PYR->PYR_NMDA',
]

param_space = {"netParams.connParams.{}.weight".format(k) : tune_range for k in params}

TARGET = pandas.Series(
    {'PYR': 3.33875,
     'BC' : 19.725,
     'OLM': 3.47,}
)

def sge_run(config):
    sge = Submit(submit_template = "qsub {cwd}/{label}.sh", script_template = template)
    dispatcher = SFSDispatcher(cwd = cwd, env = {}, submit = sge)
    dispatcher.add_dict(value_type="FLOAT", dictionary = config)
    dispatcher.run()
    data = dispatcher.get_run()
    while not data:
        data = dispatcher.get_run()
        time.sleep(5)
    dispatcher.clean(args='rswo')
    data = pandas.read_json(data, typ='series', dtype=float)
    loss = numpy.square( TARGET - data[ ['PYR', 'BC', 'OLM'] ] ).mean()
    conf_report = data[ params ].to_dict()
    report = {'loss': loss, 'PYR': data['PYR'], 'BC': data['BC'], 'OLM': data['OLM']}
    report.update(conf_report)
    session.report(report)

ray.init(
    runtime_env={"working_dir": ".", # needed for import statements
                 "excludes": ["*.csv", "*.out", "*.run",
                              "*.sh", "*.sgl",
                              ]}
)

algo = ConcurrencyLimiter(searcher=searcher, max_concurrent=CONCURRENCY, batch= True)

print("====={} search=====")
print(param_space)

tuner = tune.Tuner(
    sge_run, #objective (on machine) sge_objective (on submit)
    tune_config=tune.TuneConfig(
        search_alg=algo,
        metric="loss",
        mode="min",
        num_samples=NTRIALS,
    ),
    run_config=air.RunConfig(
        local_dir="../ray_ses",
        name=ALGORITHM,
    ),
    param_space=param_space,
)

results = tuner.fit()

resultsdf = results.get_dataframe()

resultsdf.to_csv(SAVESTR)

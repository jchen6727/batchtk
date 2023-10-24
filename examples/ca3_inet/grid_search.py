import ray
import pandas
import json
import os
import numpy
from ray import tune
from ray import air
from ray.air import session
from ray.tune.search.basic_variant import BasicVariantGenerator

from pubtk.runtk.dispatchers import INET_Dispatcher
from pubtk.runtk.submit import SGESubmitINET

import time

sge = SGESubmitINET()

sge.update_template(
    command = "time mpiexec -np $NSLOTS -hosts $(hostname) nrniv -python -mpi init.py",
    cores = "5",
    vmem = "32G"
)

CONCURRENCY = 9
SAVESTR = 'grid.csv'

cwd = os.getcwd()

grid = {'cfg.AMPA': tune.grid_search([0.5, 1.00, 1.5]),
        'cfg.GABA': tune.grid_search([0.5, 1.00, 1.5]),
        'cfg.NMDA': tune.grid_search([0.5, 1.00, 1.5]),
        }

ray.init(
    runtime_env={"working_dir": ".", # needed for import statements
                 "excludes": ["*.csv", "*.out", "*.run",
                              "*.sh" , "*.sgl", ]}
)

TARGET = pandas.Series(
    {'PYR': 3.33875,
     'BC' : 19.725,
     'OLM': 3.47,}
)
def sge_run(config):
    dispatcher = INET_Dispatcher(cwd = cwd, env = {}, submit = sge)
    dispatcher.add_dict(value_type="FLOAT", dictionary = config)
    dispatcher.run()
    tid = tune.get_trial_id()
    tno = int(tid.split('_')[-1])
    dispatcher.accept()
    data = dispatcher.recv(1024)
    dispatcher.clean(args='k')
    data = pandas.read_json(data, typ='series', dtype=float)
    loss = numpy.square( TARGET - data[ ['PYR', 'BC', 'OLM'] ] ).mean()
    strc = str(config)
    curr = os.getcwd().split('/')[-1]
    #session.report({'loss': 0, 'data': data})
    #session.report({'loss': loss, 'port': dispatcher.port, 'cwd': os.getcwd(), 'pid': os.getpid(),
    #                'PYR': data['PYR'], 'BC': data['BC'], 'OLM': data['OLM'], 
    #                'AMPA': data['cfg.AMPA'], 'GABA': data['cfg.GABA'], 'NMDA': data['cfg.NMDA']})
    session.report({'loss': loss, 'port': dispatcher.port, 'cwd': curr, 'pid': os.getpid(),
                    'strc': strc, 'id': tid, 'tno': tno,
                    'AMPA': data['cfg.AMPA'], 'GABA': data['cfg.GABA'], 'NMDA': data['cfg.NMDA']})
    
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


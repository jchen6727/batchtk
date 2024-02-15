import ray
import pandas
import os
from ray import tune, train
from ray.air import session, RunConfig
from ray.tune.search.basic_variant import BasicVariantGenerator

from pubtk.runtk.dispatchers import dispatchers
from pubtk.runtk.submits import submits

def ray_grid_search(dispatcher_type = 'zsh', submission_type = 'inet', label = 'grid', params = None, concurrency = 1, checkpoint_dir = '../grid', batch_config = None):
    ray.init(
        runtime_env={"working_dir": ".", # needed for python import statements
                     "excludes": ["*.csv", "*.out", "*.run",
                                  "*.sh" , "*.sgl", ]}
    )
    #TODO class this object for self calls? cleaner? vs nested functions
    #TODO clean up working_dir and excludes
    algo = BasicVariantGenerator(max_concurrent=concurrency)
    submit = submits[dispatcher_type][submission_type]()
    submit.update_templates(
        **batch_config
    )
    cwd = os.getcwd()
    def run(config):
        tid = ray.train.get_context().get_trial_id()
        tid = int(tid.split('_')[-1]) #integer value for the trial
        dispatcher = dispatchers[dispatcher_type](cwd = cwd, submit = submit, gid = '{}_{}'.format(label, tid))
        dispatcher.update_env(dictionary = config)
        try:
            dispatcher.run()
            dispatcher.accept()
            data = dispatcher.recv(1024)
            dispatcher.clean([])
        except Exception as e:
            dispatcher.clean([])
            raise(e)
        data = pandas.read_json(data, typ='series', dtype=float)
        session.report({'loss': 0, 'data': data})

    tuner = tune.Tuner(
        run,
        tune_config=tune.TuneConfig(
            search_alg=algo,
            num_samples=1, # grid search samples 1 for each param
            metric="loss"
        ),
        run_config=RunConfig(
            #storage_path=checkpoint_dir,
            name="grid",
        ),
        param_space=params,
    )

    results = tuner.fit()
    resultsdf = results.get_dataframe()
    resultsdf.to_csv("{}.csv".format(label))


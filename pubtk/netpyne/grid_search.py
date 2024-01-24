import ray
import pandas
import os
from ray import tune
from ray.air import session, RunConfig
from ray.tune.search.basic_variant import BasicVariantGenerator

from pubtk.runtk.dispatchers import INET_Dispatcher
from pubtk.runtk.submit import SGESubmitINET

job = {
    ('sge', 'inet'): (INET_Dispatcher, SGESubmitINET),
}
def ray_grid_search(submit, label, params, concurrency, batch_dir, config):
    ray.init(
        runtime_env={"working_dir": ".", # needed for import statements
                     "excludes": ["*.csv", "*.out", "*.run",
                                  "*.sh" , "*.sgl", ]}
    )
    algo = BasicVariantGenerator(max_concurrent=concurrency)
    submit = job[submit][1]()
    submit.update_templates(
        **config
    )
    def run(config):
        tid = tune.get_trial_id()
        tid = int(tid.split('_')[-1]) #integer value for the trial
        dispatcher = job[submit][0](cwd = os.getcwd(), submit = submit, gid = '{}_{}'.format(label, tid))
        dispatcher.update_env(dictionary = config)
        try:
            dispatcher.run()
            dispatcher.accept()
            data = dispatcher.recv(1024)
            dispatcher.clean()
        except Exception as e:
            dispatcher.clean()
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
            local_dir=batch_dir,
            name="grid",
        ),
        param_space=params,
    )

    results = tuner.fit()
    resultsdf = results.get_dataframe()
    resultsdf.to_csv("{}.csv".format(label))


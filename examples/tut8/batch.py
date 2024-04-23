from grid_search import ray_grid_search
from ray import tune
from pubtk.runtk.dispatchers import INETDispatcher
from pubtk.runtk.submits import ZSHSubmitSOCK

params = {'synMechTau2': [3.0, 5.0, 7.0],
          'connWeight' : [0.005, 0.01, 0.15]}

batch_cfg = {
    'command': 'python init.py',
}

ray_grid_search(dispatcher_constructor = INETDispatcher,
                submit_constructor = ZSHSubmitSOCK,
                label = 'tut8',
                params = params,
                concurrency = 9,
                checkpoint_dir = 'grid',
                batch_config = batch_cfg)

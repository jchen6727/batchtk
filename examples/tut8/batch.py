from grid_search import ray_grid_search
from ray import tune


params = {'synMechTau2': tune.grid_search([3.0, 5.0, 7.0]),
          'connWeight' : tune.grid_search([0.005, 0.01, 0.15])}

batch_cfg = {
    'command': 'python init.py',
}

ray_grid_search(dispatcher_type = 'zsh',
                submission_type = 'inet',
                label = 'tut8',
                params = params,
                concurrency = 9,
                checkpoint_dir = 'grid',
                batch_config = batch_cfg)

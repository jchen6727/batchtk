from grid_search import ray_grid_search
from ray import tune


params = {'cfg.synMechTau2': tune.grid_search([3.0, 5.0, 7.0]),
          'cfg.connWeight': tune.grid_search([0.005, 0.01, 0.15])}

batch_cfg = {
    'command': 'python init.py',
    'cores': '2',
    'vmem': '32G',
}

ray_grid_search(('sge', 'inet'),
                'tut8',
                params,
                9,
                '../tut8_batch',
                batch_cfg)

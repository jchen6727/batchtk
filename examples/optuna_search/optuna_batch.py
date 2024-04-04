from pubtk.raytk.search import ray_optuna_search #the one that allows for multiobjective optimization

from netpyne.batchtools import runtk

from ray import tune

params = {'synMechTau2': tune.uniform(3.0, 7.0), # LB
          'connWeight' : tune.uniform(0.005, 0.15)} #UB

batch_config = {'command': 'python init.py'}

Dispatcher = runtk.dispatchers.INETDispatcher
Submit = runtk.submits.ZSHSubmitSOCK

ray_study = ray_optuna_search(dispatcher_constructor = Dispatcher,
                  submit_constructor=Submit,
                  params = params,
                  batch_config = batch_config,
                  max_concurrent = 3,
                  output_path = '../batch_optuna',
                  checkpoint_path = '../optuna',
                  label = 'optuna_search',
                  num_samples = 15,
                  metric = ['S_loss', 'M_loss'],
                  mode = ['min', 'min'])

S = ray_study.results.get_best_result('S_loss', 'min')
M = ray_study.results.get_best_result('M_loss', 'min')

study = ray_study.algo.searcher._ot_study #can call optuna vis on this.



"""
example output:

╭────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Trial name     status         synMechTau2     connWeight     iter     total time (s)     S_loss     M_loss │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ run_43deef0e   TERMINATED         4.56797      0.14795          1            1.54674          0     4.84   │
│ run_b51a6a9a   TERMINATED         4.32802      0.0613066        1            1.49207          0   190.44   │
│ run_8157c8ce   TERMINATED         4.99058      0.119546         1            1.46263          0     3.24   │
│ run_13202560   TERMINATED         5.6803       0.043961         1            1.45289          0    86.49   │
│ run_47f5b62d   TERMINATED         5.65989      0.0351965        1            1.49298          0   161.29   │
│ run_8baef536   TERMINATED         6.21355      0.0322098        1            1.45599          0   113.423  │
│ run_9a8cd3f2   TERMINATED         4.03484      0.0416349        1            1.44622          0   416.16   │
│ run_473d34fe   TERMINATED         4.89675      0.123851         1            1.47723          0     3.8025 │
│ run_04759000   TERMINATED         6.44066      0.0942789        1            1.43357          0     2.4025 │
│ run_333b7e6f   TERMINATED         6.75622      0.058532         1            1.44275          0     0.4225 │
│ run_a69f8739   TERMINATED         6.56731      0.0135902        1            1.461            0   390.062  │
│ run_1bc0dcd6   TERMINATED         4.42863      0.0873854        1            1.42461          0    72.25   │
│ run_10cf3b21   TERMINATED         6.7494       0.072818         1            1.43714          0     0.36   │
│ run_1eb4e669   TERMINATED         6.88897      0.0816654        1            1.46431          0     3.61   │
│ run_0a4dde9d   TERMINATED         6.75771      0.0723681        1            1.42565          0     0.36   │
│ run_9fa0f7c9   TERMINATED         3.14795      0.0692016        1            1.43982          0   447.322  │
│ run_1d90d47f   TERMINATED         3.31114      0.068568         1            1.48488          0   414.123  │
│ run_a8290889   TERMINATED         3.13979      0.0671086        1            1.43697          0   457.96   │
│ run_4b109b5c   TERMINATED         6.97483      0.100636         1            1.43482          0    10.89   │
│ run_131f9893   TERMINATED         6.00962      0.0982268        1            1.46806          0     0.36   │
│ run_13534a35   TERMINATED         6.95475      0.0958389        1            1.43204          0     8.1225 │
│ run_afc6908c   TERMINATED         6.16762      0.0772009        1            1.43659          0     0.25   │
│ run_6f86dd8c   TERMINATED         6.1273       0.0769742        1            1.45673          0     0.36   │
│ run_1a066bf1   TERMINATED         6.10223      0.0776986        1            1.42383          0     0.36   │
│ run_bb97c070   TERMINATED         6.56639      0.0557106        1            1.44056          0     4      │
│ run_433147dd   TERMINATED         6.57273      0.0499768        1            1.47808          0     9.3025 │
│ run_48d08151   TERMINATED         6.46627      0.0526202        1            1.46412          0     8.41   │
│ run_64097090   TERMINATED         5.67665      0.0743617        1            1.51474          0     9.61   │
│ run_e99ae8c0   TERMINATED         5.70164      0.0743052        1            1.49379          0     8.41   │
│ run_235518dd   TERMINATED         5.76407      0.0729536        1            1.4589           0     7.0225 │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

different trial:

In [13]: results.get_best_result('S_loss', 'min')
Out[13]:
Result(
  metrics={'S_loss': 0.0, 'M_loss': 7.290000000000005, 'data': S         10.20
M         10.20
S_loss     0.00
M_loss     7.29
dtype: float64},
  path='/Users/jchen/dev/colab/optuna/optuna_search/run_fc785faa_1_connWeight=0.1240,synMechTau2=6.3379_2024-03-27_13-23-31',
  filesystem='local',
  checkpoint=None
)

In [14]: results.get_best_result('S_loss', 'min').config
Out[14]: {'synMechTau2': 6.337904648767358, 'connWeight': 0.12398437976660216}

#TODO:
study object can be retrieved with
    _.algo.searcher._ot_study
In [6]: type(study.algo.searcher._ot_study)
Out[6]: optuna.study.study.Study


In [8]: mystudy = study.algo.searcher._ot_study

In [9]: optuna.visualization.plot_pareto_front(mystudy, target_names=['M_loss', 'S_loss'])

optuna.visualization.plot_param_importances(
    ...:     mystudy, target=lambda t: t.values[0], target_name="M_loss"
    ...: )
"""

from batchtk.algos.landscapes.multiobjective import get_mw4, evaluate, get_front
from batchtk.runtk import get_runner, RunConfig, get_comm
import numpy
import os
import sys
import json


#parameter_list = ['x0', 'x1'] # for network case, would be what you have in your cfg.
#outer_cfg = RunConfig(
#    {'x0': 50, 'x1': 50, 'path': False, 'batchnum': 0},
#)#TODO, define any cfg parameters as necessary here, corresponding modification to scriptMUT.py, scriptWT.py
# KEEP batchnum for labeling purposes, each grid will create 2 sets of outputs with different batchnum
# otherwise files will be clobbered
#outer_cfg.update()





DEFAULT_NUMVAR = 4 # note that the MW4 function can handle any NUMVAR.
DEFAULT_NUMOBJ = 3

runner = get_runner()
print("runner id: {}".format(id(runner)))
cfg = RunConfig({
    'X': numpy.zeros(DEFAULT_NUMVAR), 'NUMOBJ': DEFAULT_NUMOBJ # SOO or MOO ...
})
#mappings = {'X': numpy.zeros(DEFAULT_NUMVAR)}

#print(mappings)

cfg.update()

print(cfg.X)

problem = get_mw4(n_var=len(cfg.X), n_obj=cfg.NUMOBJ)

results = evaluate(problem, numpy.array([cfg.X]))

loss = { 'F{}'.format(i): result for i, result in enumerate(results['F'][0]) }
params = { 'X{}'.format(i): x for i, x in enumerate(cfg.X) }

print(params)
print(loss)

runner.send(json.dumps({**params, **loss}))
#inputs = {key: mappings[key] for key in ('x0', 'x1')}

#results = json.dumps({**mappings})
#results = json.dumps({**inputs, 'fx': fx})

#print(results)
#with get_runner() as runner:
#    print("communication runner id: {}".format(id(runner)))
#    runner.send(results)

#if 'file' in mappings:
#    file = "{}/{}.txt".format(mappings['path'], mappings['label'])
#    print("writing results to file: {}".format(file))
#    with open(file, 'w') as fptr:
#        fptr.write(results)

#def mw4_func(x0, x1, x2, x3):
#    pass

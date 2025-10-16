from batchtk.algos.landscapes.multiobjective import get_mw4, evaluate, get_front
from batchtk.runtk import get_runner, RunConfig, get_comm
import numpy, json
"""
MW4 with:
# input variables: 4
# objectives: 2
"""

DEFAULT_NUMVAR = 4 # flexible number of variables ...
DEFAULT_NUMOBJ = 2 # flexible number of objectives ...

inputs = { 'x{}'.format(i): 0.0 for i in range(DEFAULT_NUMVAR) }

runner = get_runner()

cfg = RunConfig(inputs)
print(cfg)
cfg.update()

X = numpy.array([[cfg['x{}'.format(i)] for i in range(DEFAULT_NUMVAR)]])

problem = get_mw4(n_var=DEFAULT_NUMVAR, n_obj=DEFAULT_NUMOBJ)

results = evaluate(problem, X)
loss = { 'F{}'.format(i): result for i, result in enumerate(results['F'][0]) }

params = { 'x{}'.format(i): x for i, x in enumerate(X[0]) }
runner.send(json.dumps({**params, **loss}))
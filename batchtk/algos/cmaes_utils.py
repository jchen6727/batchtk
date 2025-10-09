from cmaes import CMA
from batchtk import runtk
from batchtk.utils import SQLStorage, ScriptLogger, expand_path
from batchtk.runtk.trial import trial as runtk_trial

define cmaes_search(



from batchtk.runtk import LocalDispatcher, SHSubmitSFS
from batchtk.utils import SQLiteLogger
from batchtk.runtk.trial import trial
from header import LEN

from batchtk.runtk.trial import trial, LABEL_POINTER, PATH_POINTER

from cmaes import CMA # CMA_ES
import numpy
import os

NUM_GEN = 3

path = os.getcwd()

entries = ["fx", *["x.{}".format(i) for i in range(LEN)]]
log = SQLiteLogger(path='../rosenbrock_out', entries=entries)
# evaluation
def eval_rosenbrock(x, tid):
    cfg = { 'x.{}'.format(i): x[i] for i in range(len(x)) }
    data = trial(
        config=cfg,
        label='rosenbrock',
        tid=tid,
        dispatcher_constructor=LocalDispatcher,
        project_path=path,
        output_path='../rosenbrock_out',
        submit_constructor=SHSubmitSFS,
        dispatcher_kwargs=None,
        submit_kwargs={'command': 'python rosenbrock.py'},
        interval=1,
        log=log,
        report=('path', 'data')
    )
    return float(data['fx'])




# suggestor
optimizer = CMA(mean=numpy.zeros(LEN), sigma=1.0)
for generation in range(NUM_GEN):
    solutions = []
    for cand in range(optimizer.population_size):
        x = optimizer.ask()
        value = eval_rosenbrock(x, "{}_{}".format(generation, cand))
        solutions.append((x, value))
        print(f"#{generation} fx={value} (x={x})")
    optimizer.tell(solutions)

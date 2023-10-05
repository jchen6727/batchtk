import pandas
import time
import numpy

from ray import tune
from ray import air
from ray.air import session


from pubtk.runtk.dispatchers import SFS_Dispatcher
from pubtk.runtk.submit import Submit

template = """\
#!/bin/bash
#$ -N job{label}
#$ -pe smp 5
#$ -l h_vmem=32G
#$ -o {cwd}/{label}.run
cd {cwd}
source ~/.bashrc
export OUTFILE="{label}.out"
export SGLFILE="{label}.sgl"
{env}
time mpiexec -np $NSLOTS -hosts $(hostname) nrniv -python -mpi init.py
"""

TARGET = pandas.Series(
    {'PYR': 3.33875,
     'BC' : 19.725,
     'OLM': 3.47,}
)

def sge_run(config):
    sge = Submit(submit_template = "qsub {cwd}/{label}.sh", script_template = template)
    dispatcher = SFS_Dispatcher(cwd = cwd, env = {}, submit = sge)
    dispatcher.add_dict(value_type="FLOAT", dictionary = config)
    dispatcher.run()
    data = dispatcher.get_run()
    while not data:
        data = dispatcher.get_run()
        time.sleep(5)
    dispatcher.clean(args='rswo')
    data = pandas.read_json(data, typ='series', dtype=float)
    loss = numpy.square( TARGET - data[ ['PYR', 'BC', 'OLM'] ] ).mean()
    conf_report = data[ params ].to_dict()
    report = {'loss': loss, 'PYR': data['PYR'], 'BC': data['BC'], 'OLM': data['OLM']}
    report.update(conf_report)
    session.report(report)
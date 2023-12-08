from pubtk.runtk.dispatchers import SH_Dispatcher
from pubtk.runtk.submit import Submit
import os

cwd = os.getcwd()

config = {
    'cfg.AMPA': 1,
    'cfg.NMDA': 1,
    'cfg.GABA': 1,
    }

template = """\
#!/bin/bash
#$ -N {label}
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

sge = Submit(submit_template = "qsub {cwd}/{label}.sh", script_template = template)

dispatcher = SH_Dispatcher(cwd = cwd, submit = sge)

dispatcher.add_dict(value_type="FLOAT", dictionary=config)

dispatcher.create_job()

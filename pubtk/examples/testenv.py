from pubtk.runtk.utils import create_script
from pubtk.runtk.dispatchers import SFS_Dispatcher
import json
import os

config = {
    'netParams.connParams.PYR->BC_AMPA.weight': 1,
    'cfg.NMDA': 2
    }
          #'cfg.value': 2, 
          #'cfg.dict': json.dumps(dict(one=1, two=2))}

netm_env = {"NETM{}".format(i): 
            "{}={}".format(key, config[key]) for i, key in enumerate(config.keys())}

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

dispatcher = SFS_Dispatcher(cmdstr = 'a', cwd = os.getcwd(), env = netm_env)

dispatcher.shcreate(template, label='ca3')

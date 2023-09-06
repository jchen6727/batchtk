from pubtk.runtk.utils import create_script

import json

config = {'netParams.connParams.PYR->BC_AMPA.weight': 1,
          'cfg.flag': True, 'cfg.value': 2, 
          'cfg.dict': json.dumps(dict(one=1, two=2))}

netm_env = {"NETM{}".format(i): 
            "{}={}".format(key, config[key]) for i, key in enumerate(config.keys())}

template = """\
#!/bin/sh
#$ -N {name}
#$ -pe smp 5
#$ -l h_vmem=32G
#$ -o {path}/{name}.run
cd {path}
source ~/.bashrc
export OUTFILE="{name}.out"
export SGLFILE="{name}.sgl"
time mpiexec -np $NSLOTS -hosts $(hostname) nrniv -python -mpi init.py
"""
create_script(env = netm_env, 
              filename = 'test.sh',
              template = sh_template,
              header = '', 
              command = '',
              footer = '')


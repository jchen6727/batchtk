### Template for SGE ###
sge_template = """#!/bin/bash
#$ -cwd
#$ -N {name}
#$ -pe smp {cores}
#$ -l h_vmem={vmem}
source ~/.bashrc
export OUTFILE="{name}.out"
export SGLFILE="{name}.sgl"
{env}
{pre}{command}{post}
touch {name}.sgl
"""

# make sure to export something to .out
# e.g:
# export NETMSAVE="test.out"
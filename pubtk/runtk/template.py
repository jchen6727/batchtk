### Template for SGE ###
sge_template = """#!/bin/bash
#$ -cwd
#$ -N {name}
#$ -pe smp {cores}
#$ -l h_vmem={vmem}
source ~/.bashrc
{env}
{pre}
{command}
{post}
"""

# make sure to export something to .out
# e.g:
# export NETMSAVE="test.out"
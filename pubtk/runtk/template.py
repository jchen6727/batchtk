### Template for SGE ###
sge_template = """#!/bin/bash
#$ -cwd
#$ -N {name}
#$ -pe smp {cores}
#$ -l h_vmem={vmem}
source ~/.bashrc
export NETM="{name}.out"
{env}
{pre}
{command}
{post}
"""
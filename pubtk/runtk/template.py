### Template for SGE ###
sge_template = """#!/bin/bash
#$ -cwd
#$ -N {jobName}
#$ -pe smp {cores}
#$ -l h_vmem={vmem}
source ~/.bashrc
{env}
{pre}
{command}
{post}
"""
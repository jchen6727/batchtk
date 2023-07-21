### Template for SGE ###
sge_template = \
"""\
#!/bin/bash
#$ -N {name}
#$ -pe smp {cores}
#$ -l h_vmem={vmem}
#$ -o {cwd}{name}.run
cd {cwd}
source ~/.bashrc
export OUTFILE="{name}.out"
export SGLFILE="{name}.sgl"
{env}
{pre}{command}{post}
"""

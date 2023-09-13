sge_template = \
"""\
#!/bin/bash
#$ -N {label}
#$ -pe smp {cores}
#$ -l h_vmem={vmem}
#$ -o {cwd}/{label}.run
cd {cwd}
source ~/.bashrc
export OUTFILE="{label}.out"
export SGLFILE="{label}.sgl"
{env}
{command}
"""
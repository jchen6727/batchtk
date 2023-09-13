#!/bin/bash
########################################################################################
#
# SGE submission:
#   overwrite any of the values with flags to the qsub argument.
#   executes the command string after sge.sh
#
########################################################################################

#$ -cwd
#$ -l h_vmem=128G
#$ -pe smp 64

source ~/.bashrc

echo executing command:
echo $*
yes '' | head -n 3

$*
#!/bin/bash
#$ -N ca3_b1591a42f94648ac14b4908ce1e1a5f1
#$ -pe smp 5
#$ -l h_vmem=32G
#$ -o /ddn/jchen/dev/pubtk/pubtk/examples/ca3_b1591a42f94648ac14b4908ce1e1a5f1.run
cd /ddn/jchen/dev/pubtk/pubtk/examples/
source ~/.bashrc
export OUTFILE="ca3_b1591a42f94648ac14b4908ce1e1a5f1.out"
export SGLFILE="ca3_b1591a42f94648ac14b4908ce1e1a5f1.sgl"

export NETM0="netParams.connParams.PYR->BC_AMPA.weight=1"
export NETM1="cfg.NMDA=2"
time mpiexec -np $NSLOTS -hosts $(hostname) nrniv -python -mpi init.py

#!/bin/bash
#$ -N b1fd12227467865fa013b4f05d64b001
#$ -pe smp 5
#$ -l h_vmem=32G
#$ -o /Users/jchen/dev/pubtk/examples/b1fd12227467865fa013b4f05d64b001.run
cd /Users/jchen/dev/pubtk/examples
source ~/.bashrc
export OUTFILE="b1fd12227467865fa013b4f05d64b001.out"
export SGLFILE="b1fd12227467865fa013b4f05d64b001.sgl"

export FLOATPMAP0="cfg.AMPA=2"
export FLOATPMAP1="cfg.NMDA=0.5"
export FLOATPMAP2="cfg.GABA=1.5"
time mpiexec -np $NSLOTS -hosts $(hostname) nrniv -python -mpi init.py

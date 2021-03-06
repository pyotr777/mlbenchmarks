#!/bin/sh
#PBS -q h-short
#PBS -l select=1:mpiprocs=1:ompthreads=1
#PBS -W group_list=gi96
#PBS -l walltime=00:15:00
cd $PBS_O_WORKDIR
. /etc/profile.d/modules.sh
module load cuda9/9.0.176 openmpi/1.10.2/gnu
PROCS=1
DATETIME="$(date +%F_%H%M%S)"
echo "Reedbush-H $(hostname). P100x$PROCS $DATETIME"

cp hpcg.dat_128x128x128_60 hpcg.dat
export OMP_NUM_THREADS=1
#export CUDA_VISIBLE_DEVICES=2,3

#MPIFLAGS="--mca btl tcp,sm,self"   # just to get rid of warning on psg cluster node wo proper IB sw installed

HPCG_BIN=xhpcg-3.1_gcc_485_cuda90176_ompi_1_10_2_sm_35_sm_50_sm_60_sm_70_ver_10_8_17
nvcc --version
nvidia-smi
mpiexec -np $PROCS $MPIFLAGS ./$HPCG_BIN | tee ./results/xhpcg_2_gpu-$DATETIME-output.txt

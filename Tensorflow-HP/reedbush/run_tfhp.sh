#!/bin/bash
#PBS -q h-short
#PBS -l select=1:mpiprocs=1:ompthreads=1
#PBS -W group_list=gi96
#PBS -l walltime=00:15:00

PROCS=1
cd $PBS_O_WORKDIR
. /etc/profile.d/modules.sh
#module load intel cuda9 anaconda3
module load intel cuda9 anaconda3
export HOME=/lustre/gi96/i96005/
source activate tf-nightly
DATETIME="$(date +%F_%H%M%S)"
echo "Reedbush-H $(hostname). P100x$PROCS $DATETIME"


nvcc --version
nvidia-smi
ls -l
cd benchmarks/scripts/tf_cnn_benchmarks/
python tf_cnn_benchmarks.py --num_gpus=$PROCS --batch_size=32 --model=resnet50 --num_batches=3

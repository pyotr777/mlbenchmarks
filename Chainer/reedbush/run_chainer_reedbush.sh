#!/bin/bash
#PBS -q h-short
#PBS -l select=1:mpiprocs=1:ompthreads=1
#PBS -W group_list=gi96
#PBS -l walltime=00:15:00

EPOCHS=10
BATCH=512
cd $PBS_O_WORKDIR
. /etc/profile.d/modules.sh
#module load intel cuda9 anaconda3
module load intel cuda9 anaconda3
export HOME=/lustre/gi96/i96005/
export CHAINER_DATASET_ROOT=/lustre/gi96/i96005/chainer/dataset
source activate chainer4
DATETIME="$(date +%F_%H%M%S)"
echo "Reedbush-H $(hostname). P100x$PROCS $DATETIME"

cd chainer/examples/cifar/
nvcc --version
nvidia-smi
pip freeze | grep -i chainer
python train_cifar.py -d cifar100 -g 0 -b $BATCH -e $EPOCHS
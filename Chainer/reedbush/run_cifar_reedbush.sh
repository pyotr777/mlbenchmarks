#!/bin/bash
#PBS -q h-short
#PBS -l select=1:mpiprocs=1:ompthreads=1
#PBS -W group_list=gi96
#PBS -l walltime=00:15:00
cd $PBS_O_WORKDIR
. /etc/profile.d/modules.sh
module load intel cuda chainer
export CHAINER_DATASET_ROOT=/lustre/gi96/i96005/chainer/dataset
pwd
ls -l
cd chainer/examples/cifar/
python train_cifar.py -d cifar100 -g 0 -b 1024 -e 10

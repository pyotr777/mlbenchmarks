#!/bin/bash
#PBS -q h-short
#PBS -l select=1:mpiprocs=1:ompthreads=1
#PBS -W group_list=gi96
#PBS -l walltime=02:00:00

EPOCHS=100
batchsizes=(32)
batchsizes=(48)
batchsizes=(64)
batchsizes=(80)
batchsizes=(128 256)
batchsizes=(384 512 640)
#batchsizes=(256 512 640)
learnrates=(0.15 0.1 0.05 0.025 0.01 0.005 0.001)
#learnrates=(0.15 0.2 0.005)

cd $PBS_O_WORKDIR
. /etc/profile.d/modules.sh

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

GPUS=2
GPU_COUNTER=0
for batchsize in "${batchsizes[@]}"; do
	for learnrate in "${learnrates[@]}"; do
		if [ $GPU_COUNTER -lt $((GPUS-1)) ]; then
			echo "gpu$GPU_COUNTER"
			echo "$GPU_COUNTER" && python train_cifar_flextime.py -d cifar100 -g $GPU_COUNTER -b $batchsize -l $learnrate -e $EPOCHS --accuracy 0.6 &
			((GPU_COUNTER++))
		else
			echo "gpu$GPU_COUNTER"
			echo "$GPU_COUNTER" && python train_cifar_flextime.py -d cifar100 -g $GPU_COUNTER -b $batchsize -l $learnrate -e $EPOCHS --accuracy 0.6
			GPU_COUNTER=0
		fi
	done
done
echo "done"

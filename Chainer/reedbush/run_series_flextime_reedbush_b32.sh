#!/bin/bash
#PBS -q h-small
#PBS -l select=1:mpiprocs=1:ompthreads=1
#PBS -W group_list=gi96
#PBS -l walltime=04:00:00

EPOCHS=100
batchsizes=(32)
# batchsizes=(48)
# batchsizes=(64)
# batchsizes=(80)
# batchsizes=(128 256)
# batchsizes=(384 512 640)
#learnrates=(0.15 0.1 0.05 0.025 0.01 0.005 0.001)
learnrates=(0.15 0.2 0.005)

cd $PBS_O_WORKDIR
. /etc/profile.d/modules.sh

module load intel cuda9 anaconda3
export HOME=/lustre/gi96/i96005/
export CHAINER_DATASET_ROOT=/lustre/gi96/i96005/chainer/dataset
source activate chainer4
DATETIME="$(date +%F_%H%M%S)"
echo "Reedbush-H $(hostname). $DATETIME"

cd chainer/examples/cifar/
nvcc --version
nvidia-smi
pip freeze | grep -i chainer

GPUS=2
# Create log files
logfiles=()
filename="stdout_$hostname"
for i in $(seq 0 $((GPUS-1))); do
	logfiles[$i]="$filename_$i.log"
	touch ${logfiles[$i]}
	echo "gpu$i, $(date)" > ${logfiles[$i]}
done

# Run jobs on GPUS
GPU_COUNTER=0
for batchsize in "${batchsizes[@]}"; do
	for learnrate in "${learnrates[@]}"; do
		echo "b$batchsize l$learnrate gpu$GPU_COUNTER" >> ${logfiles[$GPU_COUNTER]}
		if [ $GPU_COUNTER -lt $((GPUS-1)) ]; then
			python train_cifar_flextime.py -d cifar100 -g $GPU_COUNTER -b $batchsize -l $learnrate -e $EPOCHS --accuracy 0.6 >> ${logfiles[$GPU_COUNTER]}  &
			((GPU_COUNTER++))
		else
			python train_cifar_flextime.py -d cifar100 -g $GPU_COUNTER -b $batchsize -l $learnrate -e $EPOCHS --accuracy 0.6 >> ${logfiles[$GPU_COUNTER]}
			GPU_COUNTER=0
		fi
	done
done
echo "done"

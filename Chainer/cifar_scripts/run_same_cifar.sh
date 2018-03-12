#!/bin/bash

# Run Chainer CIFAR100 with different batch-sizes

batchsize=512
learnrate=0.15
EPOCHS=10
N=25

for run in $(seq 1 $N); do
	echo "run $run/$N"
	./run_cifar.sh -b $batchsize -l $learnrate -e $EPOCHS #2>/dev/null
done

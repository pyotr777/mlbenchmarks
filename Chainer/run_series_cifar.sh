#!/bin/bash

# Run Chainer CIFAR100 with different batch-sizes

batchsizes=(32 48 64 80 128 256 384 512 640)
learnrates=(0.15 0.1 0.05 0.025 0.01 0.005 0.001)
EPOCHS=10

for batchsize in "${batchsizes[@]}"; do
	for learnrate in "${learnrates[@]}"; do
		echo "b $batchsize l $learnrate"
	    ./run_cifar_determ.sh -b $batchsize -l $learnrate -e $EPOCHS #2>/dev/null
	done
done

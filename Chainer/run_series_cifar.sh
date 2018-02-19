#!/bin/bash

# Run Chainer CIFAR100 with different batch-sizes


batchsizes=(32 64 80 128 256 384 512 640 1024)
EPOCHS=10

for batchsize in "${batchsizes[@]}"; do
	echo $batchsize
    ./run_cifar.sh -b $batchsize -e $EPOCHS 2>/dev/null
done
#!/bin/bash

# Run Chainer CIFAR100 with different batch-sizes


batchsizes=(32 64 128 256 384 512 640 768 896 1024)


for batchsize in "${batchsizes[@]}"; do
	echo $batchsize
    ./run_cifar.sh -b $batchsize -e 10 2>/dev/null
done
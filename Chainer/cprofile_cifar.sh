#!/bin/bash
# Profile Chainer Cifar100 sample with cProfile

batch=64
epochs=2
logfile="cprofile_$batch.txt"
command="chainer/examples/cifar/train_cifar.py -d cifar100 -g 0 -b $batch -e $epochs"
echo "Profiling command $command"
echo "Saving to $logfile"

python -m cProfile -s tottime -o $logfile $command

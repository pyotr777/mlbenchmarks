#!/bin/bash
# Profile Chainer Cifar100 sample with nvprof

command="python chainer/examples/cifar/train_cifar.py -d cifar100 -g 0 -b 128 -e 1"
echo "Profiling command $command"
nvprof --version

nvprof $@ $command
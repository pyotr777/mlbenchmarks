#!/bin/bash
# Profile Chainer Cifar100 sample with nvprof

command="python chainer/examples/cifar/train_cifar.py -d cifar100 -g 0 -b 1024 -e 2"
echo "Profiling command $command"
nvprof --version

nvprof $@ $command
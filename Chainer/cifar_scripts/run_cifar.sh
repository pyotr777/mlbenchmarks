#!/bin/bash
# Run train_cifar sample on GPU with CIFAR100 dataset

python chainer/examples/cifar/train_cifar.py -d cifar100 -g 0 $@
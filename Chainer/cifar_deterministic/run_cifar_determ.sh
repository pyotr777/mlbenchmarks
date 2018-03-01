#!/bin/bash
# Run train_cifar sample on GPU with CIFAR100 dataset

#python chainer/examples/cifar/train_cifar_debug.py --debug -d cifar100 -g 0 $@
python chainer/examples/cifar/train_cifar_determ.py -d cifar100 -g 0 $@
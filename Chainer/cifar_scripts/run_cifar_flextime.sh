#!/bin/bash
# Run train_cifar sample on GPU with CIFAR100 dataset
# Run untill accuracy reaches 0.25

python chainer/examples/cifar/train_cifar_flextime.py -d cifar100 -g 0 $@ 2>cifar_errors.log
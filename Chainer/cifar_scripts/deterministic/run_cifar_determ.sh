#!/bin/bash
# Run train_cifar_determ.py sample with CIFAR100 dataset

N=3
for i in $(seq 1 $N);do
	python chainer/examples/cifar/train_cifar_determ.py -d cifar100 $@
done
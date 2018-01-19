#!/bin/bash

cd chainer/examples/cifar
python train_cifar.py -d cifar100 -g 0 -b 1024 -e 10
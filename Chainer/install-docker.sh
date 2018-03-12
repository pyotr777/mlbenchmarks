#!/bin/bash

# Install Chainer and Cifar benchmark in Docker container

IMAGE="nvidia/cuda:9.0-cudnn7-devel-ubuntu16.04"

nvidia-docker run -ti -v $(pwd):/root/host -p 8888 -p 80 --name chainer $IMAGE /bin/bash
#!/bin/bash

# Install python pakcages
pip install -U pip
pip install -U --user cupy #chainer

# Clone Chainer
git clone https://github.com/chainer/chainer

# Download CIFAR dataset and test Chainer
cd chainer
git checkout v4.0.0b2
pip install --user .



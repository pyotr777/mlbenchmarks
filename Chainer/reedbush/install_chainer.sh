#!/bin/bash

# Install python pakcages
pip install -U pip
pip install -U --user cupy==4.0.0b2 --no-cache-dir #chainer

# Clone Chainer
git clone https://github.com/chainer/chainer

# Download CIFAR dataset and test Chainer
cd chainer
git checkout v4.0.0b2
pip install --user . --no-cache-dir



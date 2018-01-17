#!/bin/bash

# Install Tensorflow and TF HP benchmark.
# Execute on the machine whete TF will be installed.
set -e
TF_PIP="tf-nightly-gpu"
#TF_PIP="tf"

#sudo apt-get update && sudo apt-get install -y git libcupti-dev python-pip python-dev clang

# Install TF
pip install -U pip
pip install --user $TF_PIP

# Install TF HP benchmark
if [[ ! -d benchmarks || ! -f benchmarks/scripts/tf_cnn_benchmarks/tf_cnn_benchmarks.py ]]; then
	git clone https://github.com/tensorflow/benchmarks.git
fi

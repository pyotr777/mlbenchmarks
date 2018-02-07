#!/bin/bash

# Install Tensorflow and TF HP benchmark.
# Execute on the machine whete TF will be installed.
set -e
TF_PIP="tf-nightly-gpu"

# Install TF
pip install -U pip
pip install --ignore-installed --no-cache-dir --upgrade --user $TF_PIP

# Install TF HP benchmark
if [[ ! -d benchmarks || ! -f benchmarks/scripts/tf_cnn_benchmarks/tf_cnn_benchmarks.py ]]; then
	git clone https://github.com/tensorflow/benchmarks.git
fi

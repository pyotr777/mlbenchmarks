#!/bin/bash
apt-get update && apt-get install -y git
pip install -U tf-nightly
cd /root
git clone https://github.com/tensorflow/benchmarks.git
cd benchmarks/scripts/tf_cnn_benchmarks/
pwd && ls -l
set -x
python tf_cnn_benchmarks.py  --batch_size=32 --model=resnet50 --variable_update=parameter_server

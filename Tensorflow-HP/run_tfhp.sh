#!/bin/bash

# This script will start TF HP benchmark.
cd $HOME/benchmarks/scripts/tf_cnn_benchmarks/
python tf_cnn_benchmarks.py --num_gpus=1 --batch_size=64 --model=resnet50 #--num_batches=3

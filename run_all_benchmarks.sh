#!/bin/bash

# Run all benchmarks and CUDA samples


# Install CUDA samples
cuda-install-samples-9.0.sh .
cd NVIDIA_CUDA-9.0_Samples/1_Utilities/deviceQuery/
make

# GPU and CUDA information
# Run deviceQuery
./deviceQuery
cd -

dpkg -s libcudnn7
nvidia-smi


# TF HP
./run_tfhp.sh

# HPCG
./run_hpcg.sh 1

# Chainer CIFAR100
./run_cifar.sh -e 10

# CUDA samples
cd NVIDIA_CUDA-9.0_Samples/1_Utilities/bandwidthTest
make
./bandwidthTest
cd -

cd NVIDIA_CUDA-9.0_Samples/0_Simple/matrixMulCUBLAS
make
./matrixMulCUBLAS
cd -

cd NVIDIA_CUDA-9.0_Samples/5_Simulations/nbody
make
./nbody -benchmark
./nbody -benchmark -fp64
cd -


#!/bin/bash

# Install PIP
sudo apt-get update && sudo apt-get install -y libcupti-dev python-pip python-dev

set -e
# Install CUDA
wget http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/cuda-repo-ubuntu1604_9.0.176-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu1604_9.0.176-1_amd64.deb
sudo apt-key adv --fetch-keys http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/7fa2af80.pub
sudo apt-get update && sudo apt-get install -y cuda
echo "export CUDA_ROOT=\"/usr/local/cuda-9.0\"" >> $HOME/.bashrc
echo "export PATH=\"\$PATH:\$CUDA_ROOT/bin\"" >> $HOME/.bashrc

# Install CUDNN
sudo dpkg -i libcudnn7_7.0.4.31-1+cuda9.0_amd64.deb
sudo dpkg -i libcudnn7-dev_7.0.4.31-1+cuda9.0_amd64.deb
if [[ ! -a /usr/local/cuda/include/cudnn.h ]]; then
	sudo ln -s /usr/include/cudnn.h /usr/local/cuda/include/cudnn.h
	sudo ln -s /usr/lib/x86_64-linux-gnu/libcudnn.so /usr/local/cuda/lib64/libcudnn.so
fi

# Install nvprof
sudo apt-get install nvidia-profiler

# Install python pakcages
pip install -U pip
pip install -U --user cupy chainer
set +e

# Clone Chainer
git clone https://github.com/chainer/chainer

# Download CIFAR dataset and test Chainer
cd chainer
git checkout v4.0.0b2
echo "Installation finished. Login with ssh $1 and run ./run.sh"
#set -x
#python train_cifar.py -d cifar100 -g 0 -b 1024 -e 1


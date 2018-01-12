#!/bin/bash

# Install PIP
sudo apt-get update && sudo apt-get install -y libcupti-dev python-pip python-dev

set -e
# Install CUDA 9 Toolkit
if [[ ! -f cuda-repo-ubuntu1604-9-0-local_9.0.176-1_amd64.deb ]]; then
	wget https://developer.nvidia.com/compute/cuda/9.0/Prod/local_installers/cuda-repo-ubuntu1604-9-0-local_9.0.176-1_amd64-deb
	mv cuda-repo-ubuntu1604-9-0-local_9.0.176-1_amd64-deb cuda-repo-ubuntu1604-9-0-local_9.0.176-1_amd64.deb
fi
sudo apt-key adv --fetch-keys http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/7fa2af80.pub
sudo dpkg -i cuda-repo-ubuntu1604-9-0-local_9.0.176-1_amd64.deb
sudo apt-get update
sudo apt-get install -y --allow-unauthenticated cuda


# Install CUDNN
sudo dpkg -i libcudnn7_7.0.4.31-1+cuda9.0_amd64.deb
# If not installed libcudnn7-dev_7.0.4.31-1+cuda9.0_amd64.deb Cupy complains "cuDNN is not enabled"
sudo dpkg -i libcudnn7-dev_7.0.4.31-1+cuda9.0_amd64.deb
if [[ ! -a /usr/local/cuda/include/cudnn.h ]]; then
	sudo ln -s /usr/include/cudnn.h /usr/local/cuda/include/cudnn.h
	sudo ln -s /usr/lib/x86_64-linux-gnu/libcudnn.so /usr/local/cuda/lib64/libcudnn.so
fi

export LD_LIBRARY_PATH="/usr/local/cuda/lib64:$LD_LIBRARY_PATH"
export PATH="$PATH:/usr/local/cuda/bin"
echo "export LD_LIBRARY_PATH=/usr/local/cuda/lib64:\$LD_LIBRARY_PATH" >> $HOME/.bashrc
echo "export PATH=\$PATH:/usr/local/cuda/bin" >> $HOME/.bashrc

# Install python pakcages
pip install -U pip
pip install -U --user cupy chainer
set +e

# Clone Chainer
git clone https://github.com/chainer/chainer

# Download CIFAR dataset and test Chainer
cd chainer
git checkout v4.0.0b2



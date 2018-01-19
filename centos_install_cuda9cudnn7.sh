#!/bin/bash

#sudo yum -y install epel-release dkms libstdc++.i686
sudo yum -y install kernel-devel-$(uname -r) kernel-headers-$(uname -r)

# Install PIP
sudo yum -y install python-pip python-devel

# Install CUDA 9.0
CUDA9="http://developer.download.nvidia.com/compute/cuda/repos/rhel7/x86_64/cuda-repo-rhel7-9.0.176-1.x86_64.rpm"
#CUDA9="http://developer.download.nvidia.com/compute/cuda/repos/rhel7/x86_64/cuda-repo-rhel7-9.1.85-1.x86_64.rpm" CUDA 9.1
# Alternative : runtime installation method
# CUDA9="https://developer.nvidia.com/compute/cuda/9.1/Prod/local_installers/cuda_9.1.85_387.26_linux"
FILENAME=$(basename $CUDA9)

set -e
# Install CUDA 9 Toolkit
if [[ ! -f $FILENAME ]]; then
	wget $CUDA9
fi

# For runtime CUDA installation method
#sudo sh cuda_9.1.85_387.26_linux.run

wget "https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1404/x86_64/7fa2af80.pub"
sudo rpm --import 7fa2af80.pub
sudo rpm -i $FILENAME
# warning: cuda-repo-rhel7-9.0.176-1.x86_64.rpm: Header V3 RSA/SHA512 Signature, key ID 7fa2af80: NOKEY
sudo yum clean all
sudo yum install cuda


set -e
# Install CUDNN
# cuDNN v7.0.5 Library for Linux for CUDA 9.0
CUDNN="cudnn-9.0-linux-x64-v7.tgz"
sudo cp $CUDNN /usr/local
sudo cd /usr/local
sudo tar -xzvf $CUDNN
sudo $CUDNN
sudo ldconfig

if [[ ! -a /usr/local/cuda/include/cudnn.h ]]; then
	sudo ln -s /usr/include/cudnn.h /usr/local/cuda/include/cudnn.h
	sudo ln -s /usr/lib/x86_64-linux-gnu/libcudnn.so /usr/local/cuda/lib64/libcudnn.so
fi
set +e

cudainpath=$(echo $PATH | grep -i cuda)
if [[ -z "$cudainpath" ]];then
	export PATH="$PATH:/usr/local/cuda/bin"
	echo "export PATH=\$PATH:/usr/local/cuda/bin" >> $HOME/.bashrc
fi
cudainldpath=$(echo $LD_LIBRARY_PATH | grep -i cuda/lib64)
if [[ -z "$cudainldpath" ]]; then
	export LD_LIBRARY_PATH="/usr/local/cuda/lib64:$LD_LIBRARY_PATH"
	echo "export LD_LIBRARY_PATH=/usr/local/cuda/lib64:\$LD_LIBRARY_PATH" >> $HOME/.bashrc
fi


#sudo apt-get update && sudo apt-get install -y libcupti-dev python-pip python-dev

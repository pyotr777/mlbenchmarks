#!/bin/bash

#sudo yum -y install epel-release dkms libstdc++.i686
sudo yum -y install kernel-devel-$(uname -r) kernel-headers-$(uname -r)

# Install PIP
sudo yum -y install python-pip python-devel

# Install CUDA 9.0
#CUDA9="http://developer.download.nvidia.com/compute/cuda/repos/rhel7/x86_64/cuda-repo-rhel7-9.0.176-1.x86_64.rpm"
CUDA9="https://developer.nvidia.com/compute/cuda/9.0/Prod/local_installers/cuda_9.0.176_384.81_linux-run"
CUDA_INSTALLER="cuda_9.0.176_384.81_linux.run"
#CUDA9="http://developer.download.nvidia.com/compute/cuda/repos/rhel7/x86_64/cuda-repo-rhel7-9.1.85-1.x86_64.rpm" CUDA 9.1
# Alternative : runtime installation method
# CUDA9="https://developer.nvidia.com/compute/cuda/9.1/Prod/local_installers/cuda_9.1.85_387.26_linux"
RUNFILE=$(basename $CUDA9)

set -e
# Install CUDA 9 Toolkit
if [[ ! -f $CUDA_INSTALLER ]]; then
	wget $CUDA9
	mv $RUNFILENAME $CUDA_INSTALLER
fi
sudo sh $CUDA_INSTALLER --silent --driver --toolkit --verbose

# For runtime CUDA installation method
#sudo sh cuda_9.1.85_387.26_linux.run

# if [[ ! -a 7fa2af80.pub ]]; then
# 	wget "https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1404/x86_64/7fa2af80.pub"
# fi
# set +e
# sudo rpm --import 7fa2af80.pub
# sudo rpm -i $FILENAME
# set -e
# # warning: cuda-repo-rhel7-9.0.176-1.x86_64.rpm: Header V3 RSA/SHA512 Signature, key ID 7fa2af80: NOKEY
# sudo yum clean all
# sudo yum install cuda-9.0.176-1


set -e
# Install CUDNN
# cuDNN v7.0.5 Library for Linux for CUDA 9.0
CUDNN="cudnn-9.0-linux-x64-v7.tgz"
tar -xzvf $CUDNN
sudo cp cuda/include/cudnn.h /usr/local/cuda/include
sudo cp cuda/lib64/libcudnn* /usr/local/cuda/lib64
sudo chmod a+r /usr/local/cuda/include/cudnn.h
rm -rf cuda
sudo ldconfig

if [[ ! -a /usr/local/cuda/include/cudnn.h ]]; then
	sudo ln -s /usr/include/cudnn.h /usr/local/cuda/include/cudnn.h
	sudo ln -s /usr/local/cuda-9.0/targets/x86_64-linux/lib/libcudnn.so /usr/local/cuda/lib64/libcudnn.so
fi
set +e

cudainpath=$(echo $PATH | grep -i cuda)
if [[ -z "$cudainpath" ]];then
	export PATH="$PATH:/usr/local/cuda-9.0/bin"
	echo "export PATH=\$PATH:/usr/local/cuda-9.0/bin" >> $HOME/.bashrc
fi
cudainldpath=$(echo $LD_LIBRARY_PATH | grep -i cuda/lib64)
if [[ -z "$cudainldpath" ]]; then
	export LD_LIBRARY_PATH="/usr/local/cuda-9.0/lib64:$LD_LIBRARY_PATH"
	echo "export LD_LIBRARY_PATH=/usr/local/cuda-9.0/lib64:\$LD_LIBRARY_PATH" >> $HOME/.bashrc
	echo "export LIBRARY_PATH=/usr/local/cuda-9.0/lib64/" >> $HOME/.bashrc
	echo "export CPATH=/usr/local/cuda-9.0/include/" >> $HOME/.bashrc
fi


#sudo apt-get update && sudo apt-get install -y libcupti-dev python-pip python-dev

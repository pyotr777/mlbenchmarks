#!/bin/bash

CUDA_deb="cuda-repo-ubuntu1604-9-0-local_9.0.176-1_amd64.deb"
#cuDNN="libcudnn7_7.0.4.31-1+cuda9.0_amd64.deb"
cuDNN="libcudnn7_7.0.5.15-1+cuda9.0_amd64.deb"
cuDNNdev="libcudnn7-dev_7.0.5.15-1+cuda9.0_amd64.deb"

# Install PIP
sudo apt-get update && sudo apt-get install -y libcupti-dev python-pip python-dev

set -e
# Install CUDA 9 Toolkit
if [[ ! -f "$CUDA_deb" ]]; then
	echo "Downloading CUDA local installer"
	wget https://developer.nvidia.com/compute/cuda/9.0/Prod/local_installers/cuda-repo-ubuntu1604-9-0-local_9.0.176-1_amd64-deb
	mv cuda-repo-ubuntu1604-9-0-local_9.0.176-1_amd64-deb "$CUDA_deb"
fi
echo "Installing CUDA Toolkit 9.0"
sudo apt-key adv --fetch-keys http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/7fa2af80.pub
sudo dpkg -i "$CUDA_deb"
sudo apt-get update
sudo apt-get install -y --allow-unauthenticated cuda

# Install CUDNN
echo "Installing cuDNN 7"
sudo dpkg -i "$cuDNN"
# If not installed libcudnn7-dev_7.0.4.31-1+cuda9.0_amd64.deb Cupy complains "cuDNN is not enabled"
sudo dpkg -i "$cuDNNdev"
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


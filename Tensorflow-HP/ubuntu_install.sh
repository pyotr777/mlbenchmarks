#!/bin/bash

# Install required packages to run Tensorflow and TF HP benchmark.
# Execute on remote machine whete TF will be installed.
set -x

sudo apt-get update && sudo apt-get install -y git libcupti-dev python-pip python-dev clang

# Install CUDA 8
#if [[ ! -f cuda-repo-ubuntu1604_8.0.61-1_amd64.deb ]]; then
#	wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/cuda-repo-ubuntu1604_8.0.61-1_amd64.deb
#fi
#sudo dpkg -i cuda-repo-ubuntu1604_8.0.61-1_amd64.deb
#sudo apt-get update
#sudo apt-get install -y cuda-8-0

# Install CUDA 9 Toolkit
if [[ ! -f cuda-repo-ubuntu1604-9-0-local_9.0.176-1_amd64.deb ]]; then
	wget https://developer.nvidia.com/compute/cuda/9.0/Prod/local_installers/cuda-repo-ubuntu1604-9-0-local_9.0.176-1_amd64-deb
	mv cuda-repo-ubuntu1604-9-0-local_9.0.176-1_amd64-deb cuda-repo-ubuntu1604-9-0-local_9.0.176-1_amd64.deb
fi
sudo dpkg -i cuda-repo-ubuntu1604-9-0-local_9.0.176-1_amd64.deb
sudo apt-get update
sudo apt-get install -y --allow-unauthenticated cuda

# Use CUDA
export LD_LIBRARY_PATH="/usr/local/cuda/lib64:$LD_LIBRARY_PATH"
export PATH="$PATH:/usr/local/cuda/bin"
echo "export LD_LIBRARY_PATH=/usr/local/cuda/lib64:\$LD_LIBRARY_PATH" >> $HOME/.bashrc
echo "export PATH=\$PATH:/usr/local/cuda/bin" >> $HOME/.bashrc

# Install CUDNN 7
sudo dpkg -i libcudnn7_7.0.4.31-1+cuda9.0_amd64.deb

# Install TF
pip install -U pip
pip install --user tf-nightly-gpu

INSTALL_FROM_SOURCE=""

if [[ -n $INSTALL_FROM_SOURCE ]]; then


	# Install TF from source


	# Install cudNN
	sudo dpkg -i libcudnn6_6.0.21-1+cuda8.0_amd64.deb
	#sudo dpkg -i libcudnn6-dev_6.0.21-1+cuda8.0_amd64.deb

	# Install Bazel
	sudo apt-get install -y openjdk-8-jdk
	echo "deb [arch=amd64] http://storage.googleapis.com/bazel-apt stable jdk1.8" | sudo tee /etc/apt/sources.list.d/bazel.list
	curl https://bazel.build/bazel-release.pub.gpg | sudo apt-key add -
	sudo apt-get update && sudo apt-get install -y bazel
	sudo apt-get upgrade -y bazel

	sudo apt-get install -y python-numpy python-wheel



	# Get CUDA Capability number
	cuda-install-samples-9.0.sh .
	cd NVIDIA_CUDA-9.0_Samples/1_Utilities/deviceQuery
	make
	./deviceQuery | grep -i capability
	cd -
	git clone https://github.com/tensorflow/tensorflow
	cd tensorflow
	./configure
	bazel build --config=opt --config=cuda //tensorflow/tools/pip_package:build_pip_package
	bazel-bin/tensorflow/tools/pip_package/build_pip_package /tmp/tensorflow_pkg
	ls -l /tmp/tensorflow_pkg/
	pip install --user /tmp/tensorflow_pkg/tensorflow-1.4.0-py2-none-any.whl
fi


# Install TF HP benchmark
if [[ ! -d benchmarks || ! -f benchmarks/scripts/tf_cnn_benchmarks/tf_cnn_benchmarks.py ]]; then
	git clone https://github.com/tensorflow/benchmarks.git
fi

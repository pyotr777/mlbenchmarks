# TensorFlow HP benchmark
[github.com/tensorflow/benchmarks ](https://github.com/tensorflow/benchmarks/tree/master/scripts/tf_cnn_benchmarks)

This script can be used to install and run TensorFlow HP benchmark for CPU and NVIDIA GPU. The benchmark is run inside Docker container. For benchmarking NVIDIA GPU use nvidia-docker. 

## Usage outline

1. Install nvidia-docker (or Docker for benchmarking CPU)
2. Run script.

## Instructions

### 1. nvidia-docker installation

Install docker and nvidia-docker. You can use [nvidia\_docker\_install scripts](https://github.com/pyotr777/nvidia_docker_install) for easy nvidia-docker installation on a remote machine with Debian/Ubuntu. To do that clone the repo on your local machine with

```
git clone https://github.com/pyotr777/nvidia_docker_install.git
```

and run

```
cd nvidia_docker_install 
./install_nvdocker_ubuntu.sh <remote address>
```

\<remote address\> should work with ssh: `ssh <remote address>`.

After installation is complete add your user on the remote machine to *docker* group with  `sudo usermod -a -G docker ubuntu`. Replace "ubuntu" with your user name.

### 2. Running benchmarks
Copy run.sh to the remote machine. Use the script to install and run benchmarks. 

```
Usage:
$0 [-d <docker command>] [-n/--num_gpus <int>] [--batch_size <int>] [...]

Options:
	-d					Docker command: docker / nvidia-docker.
	-n, --num_gpus 		Number of GPUs to use for tests. 0 - use CPU only.
	-b, --batch_size	Batch size
	--model				resnet50, inception3, vgg16, alexnet
	--local_parameter_device gpu/cpu
	--variable_update	The method for managing variables: parameter_server ,replicated, distributed_replicated, independent
	--use_nccl			True/False
	-h, --help			This help info.
	--debug				Print debug info.
```	

For example, to run the benchmark with nvidia-docker for 2 GPUs using batch size 64 execute:

```
./run.sh --debug -n 2 -d nvidia-docker -b 64
```

By default the benchmark will use resnet50 model with synthetic data.

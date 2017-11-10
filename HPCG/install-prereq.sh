#!/bin/bash
# Install MPI, NVIDIA drivers and CUDA
set -x
sudo apt-get update
sudo apt-get install -y libcr-dev openmpi-bin openmpi-common wget git libomp-dev
wget http://us.download.nvidia.com/tesla/384.81/nvidia-diag-driver-local-repo-ubuntu1604-384.81_1.0-1_amd64.deb
sudo apt-key add /var/nvidia-diag-driver-local-repo-384.81/7fa2af80.pub
sudo dpkg -i nvidia-diag-driver-local-repo-ubuntu1604-384.81_1.0-1_amd64.deb
sudo apt-get update
sudo apt-get install -y cuda-drivers
# CUDA 9
wget https://developer.nvidia.com/compute/cuda/9.0/Prod/local_installers/cuda-repo-ubuntu1604-9-0-local_9.0.176-1_amd64-deb
mv cuda-repo-ubuntu1604-9-0-local_9.0.176-1_amd64-deb cuda-repo-ubuntu1604-9-0-local_9.0.176-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu1604-9-0-local_9.0.176-1_amd64.deb
#sudo apt-key add /var/cuda-repo-<version>/7fa2af80.pub
sudo apt-get update
sudo apt-get install -y --allow-unauthenticated cuda
echo "export PATH=/usr/local/cuda-9.0/bin/:$PATH" >> $HOME/.bashrc
echo "export LD_LIBRARY_PATH=/usr/local/cuda-9.0/lib:$LD_LIBRARY_PATH" >> $HOME/.bashrc

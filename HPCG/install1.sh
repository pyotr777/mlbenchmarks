#!/bin/bash
# Install MPI and NVIDIA drivers
set -x
sudo apt-get update
sudo apt-get install -y libcr-dev mpich wget git libomp-dev
wget http://us.download.nvidia.com/tesla/384.81/nvidia-diag-driver-local-repo-ubuntu1604-384.81_1.0-1_amd64.deb
sudo apt-key add /var/nvidia-diag-driver-local-repo-384.81/7fa2af80.pub
sudo dpkg -i nvidia-diag-driver-local-repo-ubuntu1604-384.81_1.0-1_amd64.deb
sudo apt-get update
sudo apt-get install -y cuda-drivers
#!/bin/bash
# Install MPI

sudo apt-get update
sudo apt-get install -y libcr-dev openmpi-bin openmpi-doc libopenmpi-dev openmpi-common wget git libomp-dev
# Check OpenMPI version
ompi_info | grep -i "Open MPI:"

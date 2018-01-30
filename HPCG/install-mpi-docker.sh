#!/bin/bash
# Install MPI

apt-get update && apt-get install -y libcr-dev openmpi-bin openmpi-doc libopenmpi-dev openmpi-common wget git libomp-dev
# Check OpenMPI version
ompi_info | grep -i "Open MPI:"

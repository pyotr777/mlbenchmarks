#!/bin/bash

# Install TAU with MPI and CUDA support for Dynamic instrumentation with tau_exec.
# For use in EC2 instances.

sudo apt-get update && sudo apt-get install -y gfortran zlib1g-dev

TAU_DIR="$HOME/TAU"
echo "Installing TAU into $TAU_DIR"

CUDA_DIR=/usr/local/cuda
CONFIGURE_OPTIONS="-arch=x86_64 -prefix=$TAU_DIR -mpi -openmp -cuda=$CUDA_DIR -bfd=download -mpiinc=/usr/lib/openmpi/include/ -mpilib=/usr/lib/openmpi/lib/"
BINUTIL_DISTR_TAR="binutils-2.23.2.tar.gz"

if [[ ! -f "tau.tgz" ]]; then
    echo "Downloading TAU archive"
    wget http://tau.uoregon.edu/tau.tgz
fi
TAU_SRC="$(tar -tf tau.tgz | head -1 | awk -F'/' '{print $2}')"

if [[ ! -d "$TAU_SRC" || ! -f "$TAU_SRC/configure" ]]; then
    echo "Extracting TAU distribution files into $TAU_SRC"
    tar -xzf tau.tgz
fi

# Copy binutils if already downloaded
if [[ -f "$BINUTIL_DISTR_TAR" ]]; then
    echo "Using downloaded binutils $BINUTIL_DISTR_TAR"
    mkdir -p "$TAU_SRC/external_dependencies"
    cp "$BINUTIL_DISTR_TAR" "$TAU_SRC/external_dependencies/$BINUTIL_DISTR_TAR"
fi

# Install OpenMPI
if [[ -z "$(ompi_info 2>/dev/null)" ]]; then
    sudo apt-get install -y openmpi-bin openmpi-common libopenmpi-dev libopenmpi1.10
fi

cd $TAU_SRC
set -x
./configure $CONFIGURE_OPTIONS
make cleanall
make
export PATH="$PATH:$TAU_DIR/x86_64/bin"
make install
echo "TAU installed into $TAU_DIR"

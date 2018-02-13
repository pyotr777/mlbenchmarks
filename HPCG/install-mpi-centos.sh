#!/bin/bash
# Install MPI

MPI_ARC="openmpi-1.10.3.tar.gz"
SRC_DIR="openmpi_src"

wget "https://www.open-mpi.org/software/ompi/v1.10/downloads/$MPI_ARC" --no-check-certificate

mkdir $SRC_DIR
tar -xxvf $MPI_ARC -C $SRC_DIR --strip 1
cd $SRC_DIR
./configure --prefix=/usr/local/openmpi-1.10.3 CC=gcc CXX=g++ --enable-mpi-cxx --enable-mpi-cxx-seek
make -j $(nproc)
make install

echo "export MPIROOT=/usr/local/openmpi-1.10.3" >> $HOME/.bashrc
echo "export PATH=\$MPIROOT/bin:\$PATH" >> $HOME/.bashrc
echo "export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:\$MPIROOT/lib"  >> $HOME/.bashrc
# Check OpenMPI version
ompi_info | grep -i "Open MPI:"

#!/bin/bash

# Install HPCG

if [ ! -d hpcg ]; then
	git clone https://github.com/hpcg-benchmark/hpcg.git
fi
cd hpcg
if [ ! -d build ]; then
	mkdir build
fi
cd build
../configure Linux_MPI
make
echo "Build finish"
ls -l bin/xhpcg

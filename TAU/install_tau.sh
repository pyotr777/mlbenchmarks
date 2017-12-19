#!/bin/bash

# Install TAU with MPI and CUDA support for Dynamic instrumentation with tau_exec.
# For use in EC2 instances.

TAU_DIR="$HOME/TAU"
echo "Installing TAU into $TAU_DIR"
CURDIR="$(pwd)"

CUDA_DIR="/usr/local/cuda"
CONFIGURE_OPTIONS="-arch=x86_64 -prefix=$TAU_DIR -mpi -openmp -cuda=$CUDA_DIR -bfd=download -mpiinc=/usr/lib/openmpi/include/ -mpilib=/usr/lib/openmpi/lib/"
CONFIGURE_OPTIONS_NOMPI="-arch=x86_64 -prefix=$TAU_DIR -openmp -cuda=$CUDA_DIR -bfd=download"
BINUTIL_DISTR_TAR="binutils-2.23.2.tar.gz"


function install_tau {
	sudo apt-get update && sudo apt-get install -y build-essential gfortran zlib1g-dev

	if [[ ! -f "tau.tgz" ]]; then
	    echo "Downloading TAU archive"
	    wget http://tau.uoregon.edu/tau.tgz
	fi
	#TAU_SRC="$(tar -tf tau.tgz | head -1 | awk -F'/' '{print $2}')"

	if [[ ! -d "$TAU_DIR" || ! -f "$TAU_DIR/configure" ]]; then
	    echo "Extracting TAU distribution files into $TAU_DIR"
	    mkdir -p $TAU_DIR
	    tar -xzf tau.tgz -C $TAU_DIR --strip-components=2
	fi

	# Copy binutils if already downloaded
	if [[ -f "$BINUTIL_DISTR_TAR" ]]; then
	    echo "Using downloaded binutils $BINUTIL_DISTR_TAR"
	    mkdir -p "$TAU_DIR/external_dependencies"
	    cp "$BINUTIL_DISTR_TAR" "$TAU_DIR/external_dependencies/$BINUTIL_DISTR_TAR"
	fi
}

function install_mpi {
	# Install OpenMPI
	if [[ -z "$(ompi_info 2>/dev/null)" ]]; then
	    sudo apt-get install -y openmpi-bin openmpi-common libopenmpi-dev libopenmpi1.10
	fi
}


if [[ -n "$1" ]]; then
    if [[ "$1" == "clean" ]]; then
        echo "**********************************"
        echo "* Clean TAU directory $TAU_DIR "
        echo "**********************************"
        rm -rf $TAU_DIR
        exit 0
    elif [[ "$1" == "x86mpi" ]]; then
    	echo "Installing TAU with MPI support into $TAU_DIR"
    	install_tau
        cd $TAU_DIR
		set -x
		./configure $CONFIGURE_OPTIONS
	elif [[ "$1" == "x86" ]]; then
    	echo "Installing TAU into $TAU_DIR"
    	install_tau
        cd $TAU_DIR
		set -x
		./configure $CONFIGURE_OPTIONS_NOMPI
	fi
	make cleanall
	make
	export PATH="$PATH:$TAU_DIR/x86_64/bin"
	echo "export PATH=\"\$PATH:$TAU_DIR/x86_64/bin\"" >> $HOME/.bashrc
	make install
	echo "TAU installed into $TAU_DIR"
	exit 0
fi

echo "Options:"
echo "  clean 	      clean installation directories"
echo "  x86           install TAU with CUDA support"
echo "  x86mpi        install TAU with CUDA and MPI support"

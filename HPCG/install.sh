#!/bin/bash

# Install HPCG on remote machine

usage=$(cat <<USAGEBLOCK
Usage:
$(basename $0) <remote_address>

USAGEBLOCK
)

if [[ $# -lt 1 ]]; then
	echo "$usage"
	exit 1
fi

if [[ $# -lt 1 ]]; then
    echo "$usage"
    exit 1
fi

ADDRESS=$1
shift

INSTALLERS=( "../ubuntu_install_cuda9cudnn7.sh" "install-mpi.sh" "install-hpcg3.1.sh")
FILES=("../CUDNN7/libcudnn7_7.0.4.31-1+cuda9.0_amd64.deb" "../CUDNN7/libcudnn7-dev_7.0.4.31-1+cuda9.0_amd64.deb" "run_hpcg.sh"  "run_tau.sh" "../comb_profile.sh")

function copy_files {
	FILES=$1
	ADDR=$2
	REMOTE_FILES=$(ssh $ADDR ls -1 2>/dev/null)
	echo "Files ${FILES[@]}"
	echo "Copy to $ADDR"
	for F in ${FILES[@]}; do
		base=$(basename $F)
		COPY="yes"
		for RF in ${REMOTE_FILES}; do
			if [[ "$base" == "$RF" ]]; then
				echo "$base exists"
				COPY=""
				continue
			fi
		done
		if [[ -n "$COPY" ]]; then
			echo "Copying $F"
			scp $F $ADDRESS:
		fi
	done
}

echo "Installing HPCG v3.1 benchmark on $ADDRESS"

copy_files $FILES $ADDRESS
copy_files $INSTALLERS $ADDRESS

set -e
ssh $ADDRESS ./ubuntu_install_cuda9cudnn7.sh
ssh $ADDRESS ./install-mpi.sh
set +e
ssh $1 sudo reboot
sleep 60
set -e
ssh $ADDRESS ./install-hpcg3.1.sh
echo "Installation finished. Login with ssh $ADDRESS and run ./run.sh"
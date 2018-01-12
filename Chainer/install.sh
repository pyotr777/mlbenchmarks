#!/bin/bash

# Install Chainer and Cifar benchmark on remote machine

usage=$(cat <<USAGEBLOCK
Usage:
$(basename $0) <remote_address>

USAGEBLOCK
)

if [[ $# -lt 1 ]]; then
    echo "$usage"
    exit 1
fi

echo "Installing Chainer and Cifar100 benchmark on $1"
FILES=("ubuntu_install.sh" "../CUDNN7/libcudnn7_7.0.4.31-1+cuda9.0_amd64.deb" "../CUDNN7/libcudnn7-dev_7.0.4.31-1+cuda9.0_amd64.deb" "run.sh" "../comb_profile.sh")
for F in ${FILES[@]}; do
	echo "Copying $F"
	scp $F $1:
done

set -ex
ssh $1 ./ubuntu_install.sh
echo "Installation finished. Login with ssh $1 and run ./run.sh"

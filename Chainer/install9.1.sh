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

ADDRESS=$1
shift

INSTALLERS=("../ubuntu_install_cuda9.1cudnn7.sh" "install_chainer.sh")
#FILES=("../CUDNN7/libcudnn7_7.0.4.31-1+cuda9.0_amd64.deb" "../CUDNN7/libcudnn7-dev_7.0.4.31-1+cuda9.0_amd64.deb" "run_cifar.sh" "../comb_profile.sh")
FILES=("../CUDNN7/libcudnn7_7.0.5.15-1+cuda9.1_amd64.deb" "../CUDNN7/libcudnn7-dev_7.0.5.15-1+cuda9.1_amd64.deb" "run_cifar.sh" "../comb_profile.sh")

set -e


function copy_files {
	ADDR=$1
	shift
	FILES=("$@")
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

echo "Installing Chainer and Cifar100 benchmark on $ADDRESS"

copy_files "$ADDRESS" "${FILES[@]}"
copy_files "$ADDRESS" "${INSTALLERS[@]}"


for INSTALLER in ${INSTALLERS[@]}; do
	ssh $ADDRESS ./$(basename $INSTALLER)
done
echo "Installation finished. Login with ssh $ADDRESS and run ./run_cifar.sh"

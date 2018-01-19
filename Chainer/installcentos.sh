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

INSTALLERS=("../centos_install_cuda9cudnn7.sh" "install_chainer.sh")
FILES=("../CUDNN7/cudnn-9.0-linux-x64-v7.tgz" "run_cifar.sh" "../comb_profile.sh")

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
echo "Installation finished. Login with ssh $ADDRESS and run ./run.sh"

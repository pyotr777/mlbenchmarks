#!/bin/bash

# Install all benchmarks: HPCG3.1, Tensorflow HP (tf-nightly-gpu) and Chainer v4.0.0b2

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
# Installation start time
start=$(date +%s)

echo "Installing HPCG3.1, Chainer v4.0.0b2 and Tensorflow tf-nightly-gpu on $ADDRESS."

INSTALLERS=("ubuntu_install_cuda9cudnn7.sh" "Chainer/install_chainer.sh" "HPCG/install-mpi.sh" "HPCG/install-hpcg3.1.sh" "Tensorflow-HP/install_tfhp.sh")
FILES=("CUDNN7/libcudnn7_7.0.5.15-1+cuda9.0_amd64.deb" "CUDNN7/libcudnn7-dev_7.0.5.15-1+cuda9.0_amd64.deb" "Chainer/run_cifar.sh" "comb_profile.sh" "HPCG/run_hpcg.sh" "Tensorflow-HP/run_tfhp.sh")

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

echo "Copying files..."
copy_files "$ADDRESS" "${FILES[@]}"
copy_files "$ADDRESS" "${INSTALLERS[@]}"


for INSTALLER in ${INSTALLERS[@]}; do
	ssh $ADDRESS ./$(basename $INSTALLER)
done

# Installation end time
end=$(date +%s)
elapsed=$((end-start))

echo "Installation finished in $elapsed sec. Login with ssh $ADDRESS."

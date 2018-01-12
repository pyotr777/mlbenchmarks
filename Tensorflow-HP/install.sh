#!/bin/bash

# Install TF HP benchmark on remote machine

if [[ $# -lt 1 ]]; then
    echo "Need remote address"
    exit 1
fi

INSTALLSCRIPT="ubuntu_install.sh"

FILES=("$INSTALLSCRIPT" "../CUDNN7/libcudnn7_7.0.5.15-1+cuda9.0_amd64.deb" "run.sh" "../comb_profile.sh")
for F in ${FILES[@]}; do
	echo "Copying $F"
	scp $F $1:
done
ssh $1 ./$INSTALLSCRIPT

echo "Installation script finished."

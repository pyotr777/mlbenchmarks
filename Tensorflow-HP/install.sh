#!/bin/bash

# Install TF HP benchmark on remote machine

if [[ $# -lt 1 ]]; then
    echo "Need remote address"
    exit 1
fi

remote="$1"
INSTALLSCRIPT="ubuntu_install.sh"

scp $INSTALLSCRIPT ../CUDNN7/libcudnn7_* $remote:
ssh $remote ./$INSTALLSCRIPT

echo "Installation script finished."

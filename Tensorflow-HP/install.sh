#!/bin/bash

# Install TF HP benchmark on remote machine

if [[ $# -lt 1 ]]; then
    echo "Need remote address"
    exit 1
fi

remote="$1"

scp _install.sh libcudnn6* $remote:
ssh $remote ./install_ubuntu.sh

echo "Installation script finished."

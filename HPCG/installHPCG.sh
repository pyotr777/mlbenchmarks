#!/bin/bash

# Install MPI and HPCG on remote machine

usage=$(cat <<USAGEBLOCK
Usage:
$(basename $0) <remote_address>

USAGEBLOCK
)

if [[ $# -lt 1 ]]; then
	echo "$usage"
	exit 1
fi
set -ex
echo "Installing HPCG on $1"
scp *.sh $1:
ssh $1 ./install1.sh
ssh $1 sudo reboot
sleep 35
ssh $1 ./install2.sh
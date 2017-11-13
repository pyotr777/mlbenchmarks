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

echo "Installing HPCG on $1"
scp install-prereq.sh install-hpcg3.1.sh $1:
set -ex
ssh $1 ./install-prereq.sh
set +e
ssh $1 sudo reboot
sleep 60
set -e
ssh $1 ./install-hpcg3.1.sh
scp run.sh $1:hpcg3.1/
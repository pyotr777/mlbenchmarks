#!/bin/bash

# This script will start container with mxnet/python(:gpu) image
# And run benchmarks in it.

usage=$(cat <<USAGEBLOCK
Usage:
$0 [-d <docker command>] [-n/--num_gpus <int>] [--batch_size <int>]

Options:
	-d				Docker command: docker / nvidia/docker.
	-n, --num_gpus 	Number of GPUs to use for tests. 0 - use CPU only.
	-h, --help		This help info.
	--debug			Print debug info.
USAGEBLOCK
)


# Default parameteres
DOCKER_COMMAND=docker
NUM_GPUS=0
BATCH=32



while test $# -gt 0; do
	case "$1" in
		-h | --help)
			echo $usage
			exit 0
			;;
		-d) 
			DOCKER_COMMAND="$2";shift;
			;;
		-n | --num_gpus)
			NUM_GPUS=$2;shift;
			;;
		--debug)
			debug=YES
			;;
		--)
			shift
			break;;
		-*)
			echo "Invalid option: $1"
			echo "$usage"
			exit 1;;
	esac
	shift
done	

if [ "$NUM_GPUS" -gt 0 ]; then
	IMAGE="mxnet/python:gpu"
	GPU_OPTION="--num_gpus=$NUM_GPUS"
else
	IMAGE="mxnet/python"
	GPU_OPTION=""
fi


echo "Starting GLUON container using $DOCKER_COMMAND command using $IMAGE image."

CHECK=""
if [ -n "$debug" ]; then
	CHECK="set -x"
fi

# CREATE COMMAND FILE


if [ -n "$debug" ]; then
	set -ex
fi

CONT_NAME="mxnet"

$DOCKER_COMMAND run -td --name $CONT_NAME $IMAGE 
docker cp run_incontainer.py $CONT_NAME:/root/
$DOCKER_COMMAND exec -t $CONT_NAME python  /root/run_incontainer.py

if [ -z "$debug" ]; then
	docker rm $(docker kill $CONT_NAME)
fi
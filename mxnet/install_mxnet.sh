#!/bin/bash

# This script will start container with mxnet/python:gpu image
# And run benchmarks in it.

usage=$(cat <<USAGEBLOCK
Usage:
$0 [-d <docker command>] [-n/--num_gpus <int>] [--batch_size <int>] [...]

Options:
	-d					Docker command: docker / nvidia-docker.
	-n, --num_gpus 		Number of GPUs to use for tests. 0 - use CPU only.
	-h, --help			This help info.
	--debug				Print debug info.
USAGEBLOCK
)


# Default parameteres
DOCKER_COMMAND=docker
NUM_GPUS=0
CONT_NAME=mxnet
TMP_INSTALL="setup.sh"
TEST_FILE="test.py"
TMP_FILE="run_benchmarks.sh"

if [[ $# -lt 1 ]]; then
	echo "$usage"
	exit 1
fi

while test $# -gt 0; do
	case "$1" in
		-h | --help)
			echo "$usage"
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
		--*)
			echo "Unknown option $1"
			echo "$usage"
			exit 1
			;;
	esac
	shift
done

cpu_commands=$(cat <<COMBLOCK1
import mxnet as mx
a = mx.nd.ones((2, 3))
print a
b = a * 2 + 1
print b
b.asnumpy()
print b
COMBLOCK1
)

gpu_commands=$(cat <<COMBLOCK2
import mxnet as mx
a = mx.nd.ones((2, 3), mx.gpu())
print a
b = a * 2 + 1
print b
b.asnumpy()
print b
COMBLOCK2
)
if [ "$NUM_GPUS" -gt 0 ]; then
	IMAGE="mxnet/python:gpu"
	echo "$gpu_commands" > $TEST_FILE
else
	IMAGE="mxnet/python:latest"
	echo "$cpu_commands" > $TEST_FILE
fi

if [ -n "$debug" ]; then
	set -ex
fi

if [[ -n $(docker ps -q -f "name=$CONT_NAME") ]]; then
	docker kill $CONT_NAME
fi
if [[ -n $(docker ps -a -q -f "name=$CONT_NAME") ]]; then
	docker rm $CONT_NAME
fi
$DOCKER_COMMAND run -td --name $CONT_NAME $IMAGE
$DOCKER_COMMAND cp $TEST_FILE $CONT_NAME:/root/
$DOCKER_COMMAND exec -ti $CONT_NAME python /root/$TEST_FILE


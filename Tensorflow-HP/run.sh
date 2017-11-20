#!/bin/bash

# This script will start container with tensorflow/tensorflow:latest-gpu image
# And run benchmarks in it.

usage=$(cat <<USAGEBLOCK
Usage:
$0 [-d <docker command>] [-n/--num_gpus <int>] [--batch_size <int>] [...]

Options:
	-d					Docker command: docker / nvidia-docker.
	-n, --num_gpus 		Number of GPUs to use for tests. 0 - use CPU only.
	-b, --batch_size	Batch size
	--model				resnet50, inception3, vgg16, alexnet
	--local_parameter_device gpu/cpu
	--variable_update	The method for managing variables: parameter_server ,replicated, distributed_replicated, independent
	--use_nccl			True/False
	-h, --help			This help info.
	--debug				Print debug info.
USAGEBLOCK
)


# Default parameteres
DOCKER_COMMAND=docker
NUM_GPUS=0
BATCH=32
CONT_NAME=tf
TMP_INSTALL="setup.sh"
TMP_FILE="run_benchmarks.sh"
OTHER_OPTIONS=""

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
		-b | --batch_size)
			BATCH=$2;shift;
			;;
		--debug)
			debug=YES
			;;
		--)
			shift
			break;;
		--*)
			OTHER_OPTIONS="$OTHER_OPTIONS $1=$2";shift;
			;;
	esac
	shift
done

if [ "$NUM_GPUS" -gt 0 ]; then
	IMAGE="tensorflow/tensorflow:latest-gpu"
	PIP="tf-nightly-gpu"
	GPU_OPTION="--num_gpus=$NUM_GPUS"
else
	IMAGE="tensorflow/tensorflow:latest"
	PIP="tf-nightly"
	GPU_OPTION="--device=cpu --data_format=NHWC"
fi


cont_number=$(docker ps -a -q -f name=$CONT_NAME)
if [ -n "$cont_number" ]; then
	if [ -n "$debug" ]; then
		echo "Removing existing container $CONT_NAME"
	fi
	docker kill $CONT_NAME
	docker rm $CONT_NAME
fi

echo "Starting $CONT_NAME container using $DOCKER_COMMAND command from $IMAGE image."

CHECK=""
if [ -n "$debug" ]; then
	CHECK="set -x"
fi


# CREATE COMMAND FILES
# Second one only runs benchmarks with no installations.
commands=$(cat <<COMBLOCK1
#!/bin/bash
apt-get update && apt-get install -y git
pip install -U $PIP
cd /root
git clone https://github.com/tensorflow/benchmarks.git
COMBLOCK1
)
echo "$commands" > $TMP_INSTALL
chmod +x $TMP_INSTALL

commands=$(cat <<COMBLOCK2
#!/bin/bash
cd /root/benchmarks/scripts/tf_cnn_benchmarks/
pwd && ls -l
$CHECK
python tf_cnn_benchmarks.py $GPU_OPTION --batch_size=$BATCH $OTHER_OPTIONS

COMBLOCK2
)
echo "$commands" > $TMP_FILE
chmod +x $TMP_FILE

if [ -n "$debug" ]; then
	set -ex
fi

$DOCKER_COMMAND run -td --name $CONT_NAME $IMAGE
$DOCKER_COMMAND cp $TMP_INSTALL $CONT_NAME:/root/
$DOCKER_COMMAND cp $TMP_FILE $CONT_NAME:/root/
$DOCKER_COMMAND exec -t $CONT_NAME /bin/bash -c /root/$TMP_INSTALL
$DOCKER_COMMAND exec -t $CONT_NAME /bin/bash -c /root/$TMP_FILE

if [ -z "$debug" ]; then
	rm $TMP_FILE
	rm $TMP_INSTALL
fi

#!/bin/bash

# This script will start container with tensorflow/tensorflow:latest-gpu image
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
	IMAGE="tensorflow/tensorflow:latest-gpu"
	PIP="tf-nightly-gpu"
	GPU_OPTION="--num_gpus=$NUM_GPUS"
else
	IMAGE="tensorflow/tensorflow:latest"
	PIP="tf-nightly"
	GPU_OPTION=""
fi



echo "Starting TF container using $DOCKER_COMMAND command using $IMAGE image."

CHECK=""
if [ -n "$debug" ]; then
	CHECK="set -x"
fi

# CREATE COMMAND FILE
commands=$(cat <<COMBLOCK
#!/bin/bash
apt-get update && apt-get install -y git
pip install -U $PIP
cd /root
git clone https://github.com/tensorflow/benchmarks.git
cd benchmarks/scripts/tf_cnn_benchmarks/
pwd && ls -l
$CHECK
python tf_cnn_benchmarks.py $GPU_OPTION --batch_size=$BATCH --model=resnet50 --variable_update=parameter_server

COMBLOCK
)

echo "$commands" > run_benchmarks.sh
chmod +x run_benchmarks.sh

if [ -n "$debug" ]; then
	set -ex
fi

$DOCKER_COMMAND run -td --name tf $IMAGE 
$DOCKER_COMMAND cp run_benchmarks.sh tf:/root/
$DOCKER_COMMAND exec -t tf /bin/bash -c /root/run_benchmarks.sh

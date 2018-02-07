#!/bin/bash

# This script will start TF HP benchmark.
usage=$(cat <<USAGEBLOCK
Usage:
$0 [-n/--num_gpus <int>] [--batch_size <int>] [...]

Options:
	-n, --num_gpus 		Number of GPUs to use for tests. 0 - use CPU only.
	-b, --batch_size	Batch size
	-h, --help			This help info.
	--debug				Print debug info.
USAGEBLOCK
)

# Defaults
NUM_GPUS=1
BATCH=32

while test $# -gt 0; do
	case "$1" in
		-h | --help)
			echo "$usage"
			exit 0
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

cd $HOME/benchmarks/scripts/tf_cnn_benchmarks/
python tf_cnn_benchmarks.py --num_gpus=$NUM_GPUS --batch_size=$BATCH --model=resnet50 #--data_format=NHWC #--num_batches=3

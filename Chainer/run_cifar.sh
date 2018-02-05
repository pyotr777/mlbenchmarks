#!/bin/bash

usage=$(cat <<USAGEBLOCK
Usage:
$0 [-n/--num_gpus <int>] [--batch_size <int>] [...]

Options:
	-b, --batch_size	Batch size
	-e					Epochs to run
	-h, --help			This help info.
	--debug				Print debug info.
USAGEBLOCK
)

# Defaults
EPOCHS=2
BATCH=512

while test $# -gt 0; do
	case "$1" in
		-h | --help)
			echo "$usage"
			exit 0
			;;
		-b | --batch_size)
			BATCH=$2;shift;
			;;
		-e )
			EPOCHS=$2;shift;
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


cd chainer/examples/cifar
python train_cifar.py -d cifar100 -g 0 -b $BATCH -e $EPOCHS
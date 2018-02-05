#!/bin/bash

# Run TF HP benchmark with different batch-sizes

batchsizes=(6 12 18 24 30 36 42 48 54 62)

for batchsize in "${batchsizes[@]}"; do
	./run_tfhp.sh -b $batchsize 2>/dev/null | grep "images/sec\|Batch size"
done
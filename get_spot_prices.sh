#!/bin/bash

now_time=$(date -u "+%Y-%m-%dT%H:%M:%S")
start_time=$(date -u -v-12H "+%Y-%m-%dT%H:%M:%S")

#echo $now_time
#echo $start_time
type=g3.8xlarge
filename=g38_prices.tsv

aws ec2 describe-spot-price-history --profile us --instance-types $type --product-descriptions Linux/UNIX --start-time $start_time > $filename

python plot_timeseries.py $filename
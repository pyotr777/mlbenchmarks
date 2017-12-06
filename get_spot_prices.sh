#!/bin/bash
# Get spot prices for US profile for last 12 hours.
# Instance type can be set as CLI argument. Default is g3.8xlarge.

type=g3.8xlarge
profile="us"

if [[ -n "$1" ]];then
   type="$1"
fi

if [[ -n "$2" ]]; then
	profile="$2"
fi

filename="${type}_prices.tsv"
graph="${type}_prices.pdf"
now_time=$(date -u "+%Y-%m-%dT%H:%M:%S")
start_time=$(date -u -v-12H "+%Y-%m-%dT%H:%M:%S")
start_time_local=$(date -v-12H "+%Y-%m-%dT%H:%M:%S")
echo "$start_time_local "
echo "Spot prices for $type in $profile profile for last 12 hours."
set -x
aws ec2 describe-spot-price-history --profile $profile --instance-types $type --product-descriptions Linux/UNIX --start-time $start_time > $filename

python plot_timeseries.py $filename $graph $type

open $graph

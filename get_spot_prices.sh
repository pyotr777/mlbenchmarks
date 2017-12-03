#!/bin/bash
# Get spot prices for US profile for last 12 hours.
# Instance type can be set as CLI argument. Default is g3.8xlarge.

type=g3.8xlarge

if [[ -n "$1" ]];then
   type="$1"
fi

filename="${type}_prices.tsv"
graph="${type}_prices.pdf"
now_time=$(date -u "+%Y-%m-%dT%H:%M:%S")
start_time=$(date -u -v-12H "+%Y-%m-%dT%H:%M:%S")

#echo $now_time
#echo $start_time
echo "Spot prices for $type in US profile for last 12 hours."
aws ec2 describe-spot-price-history --profile us --instance-types $type --product-descriptions Linux/UNIX --start-time $start_time > $filename

python plot_timeseries.py $filename $graph $type

open $graph

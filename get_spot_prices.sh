#!/bin/bash

now_time=$(date -u "+%Y-%m-%dT%H:%M:%S")
start_time=$(date -u -v-1d "+%Y-%m-%dT%H:%M:%S")

#echo $now_time
#echo $start_time


aws ec2 describe-spot-price-history --profile us --instance-types g3.8xlarge --start-time $start_time

#!/bin/bash

# Combined profiling with nvidia-smi and nvprof
# Parameters: command to profile

usage=$(cat <<USAGEBLOCK
Usage:
$(basename $0) <command to profile> <profile name>

USAGEBLOCK
)

SAMPLE_RATE=50 #ms

if [[ $# -lt 1 ]]; then
    echo "$usage"
    exit 1
fi

if [[ $# -lt 2 ]]; then
	echo "Need profile name"
    echo "$usage"
    exit 1
fi

command="$1"
profile="$2"
smi_trace="$profile-nvidia-smi.csv"
nvprof_trace="$profile-nvprof-gputrace-%p.csv"
echo "Using file names: $smi_trace and $nvprof_trace"

# Start nvidia-smi
echo "Starting nvidia-smi"
nvidia-smi -lms $SAMPLE_RATE --query-gpu=timestamp,name,memory.total,memory.used,utilization.gpu,utilization.memory --format=csv > $smi_trace &
#python parse_nvsmi.py nvidia-smi -q -x -lms $SAMPLE_RATE > $smi_trace &
SMI_PID=$(echo $!)
echo "Nvidia-smi started with PID $SMI_PID"
$command
kill -6 $SMI_PID
echo "nvidia-smi finished"

echo "Starting nvprof"
nvprof --csv --log-file "$nvprof_trace" --print-gpu-trace --profile-child-processes $command
echo "nvprof finished"
echo "Traces saved to $(pwd)/ $smi_trace and $nvprof_trace"
#!/bin/bash

# Combined profiling with nvidia-smi and nvprof
# Parameters: command to profile

usage=$(cat <<USAGEBLOCK
Usage:
$(basename $0) <command to profile> <profile name>

USAGEBLOCK
)

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
smi_trace="nvidia-smi-$profile.csv"
nvprof_trace="nvprof-trace-$profile-%p.csv"
echo "Using file names: $smi_trace and $nvprof_trace"

# Start nvidia-smi
echo "Starting nvidia-smi"
nvidia-smi -lms 100 --query-gpu=timestamp,name,memory.total,memory.used,utilization.gpu,utilization.memory --format=csv > $smi_trace &
SMI_PID=$(echo $!)
$command
kill $SMI_PID
echo "nvidia-smi finished"

echo "Starting nvprof"
nvprof --csv --log-file "$nvprof_trace" --print-gpu-trace --profile-child-processes $command
echo "nvprof finished"
echo "Traces saved to $(pwd)/ $smi_trace and $nvprof_trace"
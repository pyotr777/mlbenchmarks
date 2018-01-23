#!/bin/bash

# Execute on Reedbush login node
# In directory /lustre/gi96/i96005/TensorflowHP

LUSTR_HOME="/lustre/gi96/i96005"

export HOME=$LUSTR_HOME
module load anaconda3
conda create -n tf-nightly python=3
source activate tf-nightly

echo "Run: pip install -U tf-nightly-gpu --no-cache-dir"

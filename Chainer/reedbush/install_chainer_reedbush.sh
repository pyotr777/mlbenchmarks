#!/bin/bash

# Execute on Reedbush login node
# In directory /lustre/gi96/i96005/TensorflowHP

LUSTR_HOME="/lustre/gi96/i96005"

export HOME=$LUSTR_HOME
module load anaconda3 cuda9
conda create -n chainer4 python=2
source activate chainer4

echo "Run: install_chainer.sh in chainer4 environment."
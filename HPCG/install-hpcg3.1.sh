#!/bin/bash

wget http://www.hpcg-benchmark.org/downloads/hpcg-3.1_cuda9_ompi1.10.2_gcc485_sm_35_sm_50_sm_60_sm_70_ver_10_8_17.tgz
if [ ! -d hpcg3.1 ]; then
	mkdir hpcg3.1
fi
tar -xzvf hpcg-3.1_cuda9_ompi1.10.2_gcc485_sm_35_sm_50_sm_60_sm_70_ver_10_8_17.tgz -C hpcg3.1 --strip-components=1
ls -l hpcg3.1
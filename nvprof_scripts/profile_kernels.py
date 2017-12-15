#!/usr/bin/env python

import subprocess

print "profile_kernels v0.04"

# kernels = ['maxwell_scudnn_128x128_stridedB_splitK_interior_nn', 'maxwell_scudnn_128x128_relu_interior_nn', 'bn_bw_1C11_kernel_new', 'cudnn_maxwell_gcgemm_64x32_tn_batched', 'bn_fw_tr_1C11_kernel_new', 'EigenMetaKernel', 'maxwell_scudnn_128x128_stridedB_interior_nn', 'void fft2d_r2c_16x16', 'maxwell_scudnn_128x64_stridedB_splitK_interior_nn', 'maxwell_sgemm_128x64_nt', 'cudnn_maxwell_cgemm_64x64_tn_batched', 'wgrad_alg0_engine', 'SwapDimension0And2InTensor3Simple', 'void transpose_readWrite_alignment_kernel', 'implicit_convolve_sgemm', 'dgrad_engine', 'maxwell_scudnn_winograd_128x128_ldg1_ldg4_tile418n_nt', 'maxwell_scudnn_128x64_stridedB_splitK_medium_nn', 'void fft2d_c2r_16x16', 'maxwell_sgemm_128x64_nn', 'maxwell_scudnn_128x64_relu_interior_nn', 'void fft2d_r2c_64x64']
kernels = ['maxwell_scudnn_128x128_stridedB_splitK_interior_nn', 'maxwell_scudnn_128x128_relu_interior_nn']
metrics = ["dram_utilization","dram_read_throughput","dram_write_throughput"]

base_command = "python tf_cnn_benchmarks.py --num_gpus=1 --batch_size=32 --model=resnet50 --num_batches=3 --num_warmup_batches=1"
for metric in metrics:
    for kernel in kernels:
        command = "nvprof --replay-mode application --kernels '" + kernel + "'  --metrics " + metric+" --replay-mode application "+base_command
        command_split = str.split(command)
        p = subprocess.Popen(command_split, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        while p.poll() is None:
            s, serr = p.communicate()
            for s in serr.splitlines():
                print s



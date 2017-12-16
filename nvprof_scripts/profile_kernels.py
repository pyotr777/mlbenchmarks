#!/usr/bin/env python

import subprocess

print "profile_kernels v0.18"

#kernels = ['maxwell_scudnn_128x128_stridedB_splitK_interior_nn', 'maxwell_scudnn_128x128_relu_interior_nn', 'bn_bw_1C11_kernel_new', 'cudnn_maxwell_gcgemm_64x32_tn_batched', 'bn_fw_tr_1C11_kernel_new', 'EigenMetaKernel']
#kernels = ['wgrad_alg0_engine','maxwell_scudnn_128x128_stridedB_splitK_interior_nn']
metrics = ["dram_utilization","dram_read_throughput","dram_write_throughput","flop_sp_efficiency","flop_dp_efficiency","sysmem_read_throughput","sysmem_write_throughput"]

base_command = "python tf_cnn_benchmarks.py --num_gpus=1 --batch_size=32 --model=resnet50 --num_batches=3 --num_warmup_batches=1"
for metric in metrics:
    command = "nvprof --replay-mode application --csv --log-file nvprof_kernel."+metric+".log --metrics " + metric+" "+base_command
    print "\n"+command
    #command_split = str.split(command)
    p = subprocess.Popen(command,shell=True)
    while p.poll() is None:
        s, serr = p.communicate()
        print s
        print "e:",serr



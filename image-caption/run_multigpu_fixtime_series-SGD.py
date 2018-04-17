#!/usr/bin/env python

# Prepares and runs multiple tasks on multiple GPUs: one task per GPU.
# Waits if no GPUs available. For GPU availability check uses "nvidia-smi dmon" command.

# 2018 (C) Peter Bryzgalov @ CHITECH Stair Lab

from __future__ import print_function
import time
import os
import multigpuexec


gpus = range(4,8)
runs = 1
samples= 1000
time_limit = int(60 * 60 * 3.5)
tasks = []
logdir = "logs/fixtime/SGD/LRWD_time_limit"+str(time_limit)+"s"
if not os.path.exists(logdir):
    os.makedirs(logdir)
batchsizes = [40,]
learnrates=[1.05, 1.1]
weightdecay=[0.0001, 0.00001]
sss = 300
sg = 0.8
for run in range(runs):
    for batch in batchsizes:
        for lr in learnrates:
            for wd in weightdecay:
                logfile=os.path.join(logdir,"imagecaption_b{}_l{}_wd{}_smp{}_{:02d}.log".format(batch,lr,wd,samples,run))
                if os.path.isfile(logfile):
                    print("file",logfile,"exists.")
                    continue
                comm = "python train_gen_fixtime_SGD.py --early_stopping -v --scheduler_step_size {sss} --scheduler_gamma {sg} --batch_size {bs} -l {lr} --weight_decay {wd} --model resnet50 --use_samples {sm} --time_limit {tl}".format(sss=sss, sg=sg, bs=batch, lr=lr, wd=wd, sm=samples, tl=time_limit)
                print(comm)
                task = {"comm":comm,"logfile":logfile,"batch":batch,"lr":lr}
                tasks.append(task)

print("Have",len(tasks),"tasks")

gpu = -1 # Number of GPU to start check
for i in range(0,len(tasks)):
    #print "Preapare",tasks[i]["comm"],">",tasks[i]["logfile"]
    gpu = multigpuexec.getNextFreeGPU(gpus, start=gpu+1)
    gpu_info = multigpuexec.getGPUinfo(gpu)
    f = open(tasks[i]["logfile"],"w+")
    f.write("b{} l{}\n".format(tasks[i]["batch"],tasks[i]["lr"]))
    f.write("GPU: {}\n".format(gpu_info))
    f.close()
    multigpuexec.runTask(tasks[i],gpu,verbose=False)
    print("{}/{}".format(i+1,len(tasks)))
    time.sleep(5)



#!/usr/bin/env python

# Prepares and runs multiple tasks on multiple GPUs: one task per GPU.
# Waits if no GPUs available. For GPU availability check uses "nvidia-smi dmon" command.

# 2018 (C) Peter Bryzgalov @ CHITECH Stair Lab

from __future__ import print_function
import time
import os
import multigpuexec


gpus = range(0,8)
print(gpus)
runs = 2
samples= 1000
time_limit = 1800
tasks = []
logdir = "logs/fixtime/SGD/time_limit"+str(time_limit)+"s"
if not os.path.exists(logdir):
    os.makedirs(logdir)
batchsizes = [4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52]
learnrates=[0.0001, 0.0002, 0.00035, 0.0005, 0.001, 0.0025, 0.005, 0.0075, 0.01]
for run in range(runs):
    for batch in batchsizes:
        for lr in learnrates:
            logfile=os.path.join(logdir,"imagecaption_b{}_l{}_smp{}_{:02d}.log".format(batch,lr,samples,run))
            if os.path.isfile(logfile):
                print("file",logfile,"exists.")
                continue
            comm = "python train_gen_fixtime_SGD.py --early_stopping --batch_size {bs} -l {lr} --weight_decay 0.001 --model resnet50 --use_samples {sm} --time_limit {tl}".format(bs=batch, lr=lr, sm=samples, tl=time_limit)
            print(comm)
            task = {"comm":comm,"logfile":logfile,"batch":batch,"lr":lr}
            tasks.append(task)

print("Have",len(tasks),"tasks")
gpus = range(0,8)
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
    print("{}/{}".format(i,len(tasks)))
    time.sleep(5)



#!/usr/bin/env python

# Prepares and runs multiple tasks on multiple GPUs: one task per GPU.
# Waits if no GPUs available. For GPU availability check uses "nvidia-smi dmon" command.

# 2018 (C) Peter Bryzgalov @ CHITECH Stair Lab

import subprocess
import re
import time
import os

# Returns True if GPU #i is not used.
# Uses nvidia-smi command to monitor GPU SM usage.
def GPUisFree(i):
    command = "nvidia-smi dmon -c 3 -d 2 -i {} -s u".format(i)
    nvsmi_pattern = re.compile(r"^\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)")
    proc = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, shell=False)
    u = 0
    for line in iter(proc.stdout.readline, b''):
        #print line,
        m = nvsmi_pattern.match(line)
        if m:
            print ".",
            u += int(m.group(2))
    if u < 1:
        return True
    return False


# Returns number of a free GPU.
# Starts checking GPUs availability from GPU number "start".
def getNextFreeGPU(start=0):
    global gpus
    if start >= gpus:
        start = 0
    while True:
        for i in range(0,gpus):
            if start > 0 and i < start:
                #print "skip",i
                continue
            start = 0
            print "checking GPU",i,
            if GPUisFree(i):
                return i
            print "busy"
            time.sleep(5)


# Runs a task on specified GPU
def runTask(task,gpu):
    f = open(task["logfile"],"ab")
    #f.write("gpu"+str(gpu)+"\n")
    command = task["comm"]+" -g "+str(gpu)
    # IMPORTANT: remote double spaces or they will become empty arguments!
    command = re.sub('\s+',' ',command).strip()
    print "Starting ",command.split(" ")
    pid = subprocess.Popen(command.split(" "),stdout=f,bufsize=1).pid
    print pid


gpus = 8
runs = 1
batchsizes=[32, 48, 64, 80, 128, 256, 384, 512, 640, 768, 896, 1024, 1152, 1280, 1408, 1536, 1664]
#batchsizes=[256, 512]
learnrates=[0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.1, 0.05, 0.025, 0.01, 0.005, 0.001]
#learnrates=[0.1,0.01]
#epochs=100
time_limit = 1800
#acc_target = 0.6
tasks = []
logdir = "logs/fixtime/time_limit"+str(time_limit)+"s"
if not os.path.exists(logdir):
    os.makedirs(logdir)
for run in range(runs):
    for batch in batchsizes:
        for lr in learnrates:
            logfile=os.path.join(logdir,"cifar_log_b{}_l{}_{:02d}.log".format(batch,lr,run))
            if os.path.isfile(logfile):
                print "file",logfile,"exists."
                continue
            comm = "python chainer/examples/cifar/train_cifar_fixtime.py -d cifar100 -b {} -l {} --time_limit {tl}".format(batch,lr, tl=time_limit)
            print comm
            task = {"comm":comm,"logfile":logfile, "batch":batch, "lr":lr}
            tasks.append(task)

print "Have",len(tasks),"tasks"
gpu = -1
for i in range(0,len(tasks)):
    #print "Preapare",tasks[i]["comm"],">",tasks[i]["logfile"]
    gpu = getNextFreeGPU(gpu+1)
    f = open(tasks[i]["logfile"],"w+")
    f.write("b{} l{}\n".format(tasks[i]["batch"],tasks[i]["lr"]))
    f.close()
    runTask(tasks[i],gpu)
    print "{}/{}".format(i,len(tasks))
    time.sleep(5)


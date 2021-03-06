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
        print line,
        m = nvsmi_pattern.match(line)
        if m:
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
            print "checking GPU ",i
            if GPUisFree(i):
                return i
            print "busy"
            time.sleep(1)


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
batchsizes=[32, 48, 64, 80, 128, 256, 384, 512, 640]
#batchsizes=[256, 512]
learnrates=[0.15, 0.1, 0.05, 0.025, 0.01, 0.005, 0.001]
epochs=100
tasks = []
for batch in batchsizes:
    for lr in learnrates:
        logfile="logs/cifar_log_b{}_l{}.log".format(batch,lr)
        if os.path.isfile(logfile):
            print "file",logfile,"exists."
            continue
        f = open(logfile,"w+")
        f.write("b{} l{}\n".format(batch,lr))
        f.close()
        #task = {"comm":"python chainer/examples/cifar/train_cifar.py -d cifar100 -e 5 -b {} -l {} ".format(batch,lr),"logfile":logfile}
        task = {"comm":"python chainer/examples/cifar/train_cifar_flextime.py -d cifar100 -e {} --accuracy 0.6 -b {} -l {} ".format(epochs,batch,lr),"logfile":logfile}
        tasks.append(task)

print "Have",len(tasks),"tasks"
gpu = -1
for i in range(0,len(tasks)):
    #print "Preapare",tasks[i]["comm"],">",tasks[i]["logfile"]
    gpu = getNextFreeGPU(gpu+1)
    runTask(tasks[i],gpu)
    time.sleep(7)



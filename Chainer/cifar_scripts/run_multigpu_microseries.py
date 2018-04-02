#!/usr/bin/env python

# Prepares and runs multiple tasks on multiple GPUs: one task per GPU.
# Waits if no GPUs available. For GPU availability check uses "nvidia-smi dmon" command.

# 2018 (C) Peter Bryzgalov @ CHITECH Stair Lab

import subprocess
import re
import time
import os
import numpy as np
import random

# Returns True if GPU #i is not used.
# Uses nvidia-smi command to monitor GPU SM usage.
def GPUisFree(i):
    command = "nvidia-smi pmon -c 2 -d 2 -i {} -s u".format(i)
    #nvsmi_pattern = re.compile(r"^\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)") # dmon
    nvsmi_pattern = re.compile(r"^\s+(\d+)\s+([0-9\-]+)\s+([CG\-])\s+([0-9\-]+)\s")
    proc = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, shell=False)
    u = 1
    for line in iter(proc.stdout.readline, b''):
        print line,
        m = nvsmi_pattern.search(line)
        if m:
            pid = m.group(2)
            if pid == "-":
                u = 0
            else:
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
            time.sleep(5)


# Runs a task on specified GPU
def runTask(task,gpu):
    f = open(task["logfile"],"ab")
    #f.write("gpu"+str(gpu)+"\n")
    command = task["comm"]+" -g "+str(gpu)
    # IMPORTANT: remote double spaces or they will become empty arguments!
    command = re.sub('\s+',' ',command).strip()
    print "Starting ",command.split(" ")
    pid = subprocess.Popen(command.split(" "),stdout=f,stderr=None, bufsize=1).pid
    print pid


gpus = 1
runs = 2
tasks = []
for run in range(runs):
    batchsizes = random.sample(np.arange(64,900),400)
    learnrates=[0.15]
    epochs=1
    for batch in batchsizes:
        for lr in learnrates:
            logfile="logs/microseries/cifar_log_b{}_l{:.3f}_{:04d}.log".format(batch,lr,run)
            if os.path.isfile(logfile):
                print "file",logfile,"exists."
                continue

            task = {"comm":"python chainer/examples/cifar/train_cifar.py -d cifar100 -e {} -b {} -l {} ".format(epochs,batch,lr),"logfile":logfile,"batchsize":batch,"lr":lr}
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
    time.sleep(15)



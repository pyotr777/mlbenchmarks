#!/usr/bin/env python

# Prepares and runs multiple tasks on multiple GPUs: one task per GPU.
# Waits if no GPUs available. For GPU availability check uses "nvidia-smi dmon" command.

# Multiple runs with same hyper-parameters for fixed epochs.

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
batch = 512
lr = 0.15
epochs = 500
runs = 24
tasks = []
print "Running ",runs,"runs for",epochs,"epochs with batch size",batch,"and lr",lr
print "Fix LR after several reductions: 4 times reduce LR by 1/2 after 25 epochs, than fix LR."
for run in range(0,runs):
    logfile="logs/series/cifar_fixLR_e{}_run_{}.log".format(epochs,run)
    # logfile="logs/series/cifar_e{}_run_{}.log".format(epochs,run)
    # logfile="logs/series/cifar_adam_e{}_run_{}.log".format(epochs,run)
    print "Logs:",logfile
    if os.path.isfile(logfile):
        print "file",logfile,"exists."
        continue
    f = open(logfile,"w+")
    f.write("b{}\n".format(batch))
    f.close()
    task = {"comm":"python chainer/examples/cifar/train_cifar_fix_lr.py -d cifar100 -e {} -b {} -l {} ".format(epochs,batch,lr),"logfile":logfile}
    # task = {"comm":"python chainer/examples/cifar/train_cifar.py -d cifar100 -e {} -b {} -l {} ".format(epochs,batch,lr),"logfile":logfile}
    # task = {"comm":"python chainer/examples/cifar/train_cifar_adamoptimizer.py -d cifar100 -e {} -b {}".format(epochs,batch),"logfile":logfile}
    tasks.append(task)

print "Have",len(tasks),"tasks"
gpu = -1
for i in range(0,len(tasks)):
    #print "Preapare",tasks[i]["comm"],">",tasks[i]["logfile"]
    gpu = getNextFreeGPU(gpu+1)
    runTask(tasks[i],gpu)
    time.sleep(7)



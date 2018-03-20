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
    command = "nvidia-smi dmon -c 3 -d 3 -i {} -s u".format(i)
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
batchsizes=[8, 16, 24, 32, 48, 64, 80, 128, 256, 384, 512, 640, 768, 1024, 1280, 1536]
#batchsizes=[256, 512]
epochs=100
tasks = []
logfiles = []
log_dir = "logs/flextime/0_6x100/"
for batch in batchsizes:
    logfile=os.path.join(log_dir,"cifar_adam_flextime_b{}.log".format(batch))
    if os.path.isfile(logfile):
        print "file",logfile,"exists."
        continue
    logfiles.append(logfile)
    f = open(logfile,"w+")
    f.write("b{}\n".format(batch))
    f.close()
    task = {"comm":"python chainer/examples/cifar/train_cifar_flextime_adam.py -d cifar100 -e {} --accuracy 0.6 -b {}".format(epochs,batch),"logfile":logfile}
    tasks.append(task)

print "Have",len(tasks),"tasks"
gpu = -1
for i in range(0,len(tasks)):
    #print "Preapare",tasks[i]["comm"],">",tasks[i]["logfile"]
    gpu = getNextFreeGPU(gpu+1)
    runTask(tasks[i],gpu)
    time.sleep(8)

print "All tasks started.\nLogs:",logfiles


#!/usr/bin/env python

# Prepares and runs multiple tasks on multiple GPUs: one task per GPU.
# Waits if no GPUs available. For GPU availability check uses "nvidia-smi dmon" command.

# 2018 (C) Peter Bryzgalov @ CHITECH Stair Lab

import subprocess
import re
import time
import os, sys
import numpy as np
import random
import signal

# Returns True if GPU #i is not used.
# Uses nvidia-smi command to monitor GPU SM usage.
def GPUisFree(i):
    command = "nvidia-smi dmon -c 3 -d 1 -i {} -s u".format(i)
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

    # Start nvidia-smi
    trace_file = os.path.splitext(task["logfile"])[0]+".nvsmi.csv"
    fsmi = open(trace_file,"ab")
    sample_rate= 50 #ms
    print "nvidia-smi trace:",trace_file
    smi_command = "nvidia-smi -lms {sample_rate} --query-gpu=timestamp,name,memory.total,memory.used,utilization.gpu,utilization.memory --format=csv > {trace_file} &".format(sample_rate=sample_rate,trace_file=trace_file)
    smi_pid=subprocess.Popen(smi_command.split(" "),stdout=fsmi,stderr=fsmi,bufsize=1).pid
    print "nvidia-smi started with pid",smi_pid

    print "Starting ",command.split(" ")
    # pid = subprocess.Popen(command.split(" "),stdout=f,stderr=None, bufsize=1).pid
    # print pid
    p = subprocess.Popen(command.split(" "),stdout=subprocess.PIPE,stderr=None)
    for out in iter(p.stdout.readline, b''):
        if out == '' and p.poll() != None:
            break
        if out != '':
            f.write(out)
            print out,
            sys.stdout.flush()

    # Kill nvidia-smi
    os.kill(smi_pid, signal.SIGTERM)


    #  comb_profile_b{bs}_l{lr}_r{run}


gpus = 1
runs = 2
tasks = []
logdir="logs/combined_profiles/"
if not os.path.exists(logdir):
    os.makedirs(logdir)
for run in range(runs):
    batchsizes = random.sample(np.arange(64,900),400)
    learnrates=[0.15]
    epochs=1
    for batch in batchsizes:
        for lr in learnrates:
            logfile=os.path.join(logdir,"cifar_log_b{}_l{:.3f}_{:02d}.log".format(batch,lr,run))
            if os.path.isfile(logfile):
                print "file",logfile,"exists."
                continue

            task = {"comm":"python chainer/examples/cifar/train_cifar.py -d cifar100 -e {epochs} -b {bs} -l {lr}".format(epochs=epochs,bs=batch,lr=lr,run=run),"logfile":logfile,"batch":batch,"lr":lr}
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



#!/usr/bin/env python

# Prepares and runs multiple tasks on multiple GPUs: one task per GPU.
# Waits if no GPUs available. For GPU availability check uses "nvidia-smi dmon" command.

# 2018 (C) Peter Bryzgalov @ CHITECH Stair Lab

from __future__ import print_function
import subprocess
import re
import time
import os



# Returns True if GPU #i is not used.
# Uses nvidia-smi command to monitor GPU SM usage.
def GPUisFree(i):
    command = "nvidia-smi pmon -c 4 -d 1 -i {} -s u".format(i)
    #nvsmi_pattern = re.compile(r"^\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)") # dmon
    nvsmi_pattern = re.compile(r"^\s+(\d+)\s+([0-9\-]+)\s+([CG\-])\s+([0-9\-]+)\s")
    proc = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, shell=False)
    u = 1
    for line in iter(proc.stdout.readline, b''):
        line = line.decode('utf-8')
        m = nvsmi_pattern.search(line)
        if m:
            print(".",end="")
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
            print("checking GPU",i,end="")
            if GPUisFree(i):
                return i
            print("busy")
            time.sleep(5)


# Runs a task on specified GPU
def runTask(task,gpu):
    f = open(task["logfile"],"ab")
    #f.write("gpu"+str(gpu)+"\n")
    command = task["comm"]
    #command = "python --version"
    # IMPORTANT: remote double spaces or they will become empty arguments!
    command = re.sub('\s+',' ',command).strip()
    command = "NV_GPU="+str(gpu)+" ./run_container.sh "+command
    print("Starting ",command)
    pid = subprocess.Popen(command, stdout=f, stderr=f, bufsize=1, shell=True).pid
    #p = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, shell=True)
    print(pid)
    # for line in iter(p.stdout.readline,''):
    #     print(line.rstrip())


gpus = 8
runs = 2
samples= 1000
epochs = 100
loss_target = 5.4
tasks = []
logdir = "logs/flextime/loss"+str(loss_target)+"_"+str(epochs)+"epoch"
if not os.path.exists(logdir):
    os.makedirs(logdir)
batchsizes = [4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44]
learnrates=[0.0001, 0.0005, 0.001, 0.0025, 0.005, 0.0075, 0.01]
for run in range(runs):
    for batch in batchsizes:
        for lr in learnrates:
            logfile=os.path.join(logdir,"imagecaption_b{}_l{}_smp{}_{:02d}.log".format(batch,lr,samples,run))
            if os.path.isfile(logfile):
                print("file",logfile,"exists.")
                continue
            comm = "python train_gen_flextime.py --early_stopping --batch_size {bs} -l {lr} --weight_decay 0.001 --model resnet50 --use_samples {sm} --max_epoch {ep} --loss_target {target}".format(bs=batch, lr=lr, sm=samples, ep=epochs, target=loss_target)
            print(comm)
            task = {"comm":comm,"logfile":logfile,"batch":batch,"lr":lr}
            tasks.append(task)

print("Have",len(tasks),"tasks")
gpu = -1
for i in range(0,len(tasks)):
    #print "Preapare",tasks[i]["comm"],">",tasks[i]["logfile"]
    gpu = getNextFreeGPU(gpu+1)
    f = open(tasks[i]["logfile"],"w+")
    f.write("b{} l{}\n".format(tasks[i]["batch"],tasks[i]["lr"]))
    f.close()
    runTask(tasks[i],gpu)
    print("{}/{}".format(i,len(tasks)))
    time.sleep(5)



# MutliGPU series execution support
# 2018 (C) Peter Bryzgalov @ CHITECH Stair Lab

from __future__ import print_function
import subprocess
import re
import time

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


# Returns GPU info
def getGPUinfo(i,query="name,memory.total"):
    command = "nvidia-smi -i {} --query-gpu={} --format=csv,noheader".format(i,query)
    proc = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, shell=False)
    output = ""
    for line in iter(proc.stdout.readline, b''):
        line = line.decode('utf-8')
        output += line
    return output


# Returns number of a free GPU.
# gpus  -- GPU number or list of numbers.
# start -- number of GPU to start with.
def getNextFreeGPU(gpus,start=-1):
    if not isinstance(gpus,list):
        gpus = [gpus]
    if start > gpus[-1]: 
        # Rewind to GPU 0
        start = 0
    while True:
        for i in range(0,len(gpus)):
            gpu = gpus[i]
            if gpu < start:
                continue
            print("checking GPU",gpu,end="")
            if GPUisFree(gpu):
                return gpu
            print("busy")
            time.sleep(3)
            start = -1 # Next loop check from 1


# Runs a task on specified GPU
def runTask(task,gpu,verbose=False):
    f = open(task["logfile"],"ab")
    #f.write("gpu"+str(gpu)+"\n")
    command = task["comm"]
    #command = "python --version"
    # IMPORTANT: remote double spaces or they will become empty arguments!
    command = re.sub('\s+',' ',command).strip()
    command = "NV_GPU="+str(gpu)+" ./run_container.sh "+command
    print("Starting ",command)
    if not verbose:
        pid = subprocess.Popen(command, stdout=f, stderr=f, bufsize=1, shell=True).pid
        print(pid)
    else:
        p = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, shell=True)
        for line in iter(p.stdout.readline,''):
            print(line.rstrip())
            f.write(line)
    f.close()

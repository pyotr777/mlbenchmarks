#!/usr/bin/env python

# Parse nvidia-smi -q output into CSV format.
# Output line by line in real time.

# Ver. 0.9 2018/02/02
# Copyright (c) 2018 Peter Bryzgalov, Stair Lab, CHITEC


import argparse

usage='''
python parse_nvsmi.py [-h] <command>
'''

parser = argparse.ArgumentParser(usage=usage)
parser.add_argument("command", help="Command to profile with nvidia-smi",nargs='*')
args, options = parser.parse_known_args()

if args.command is None:
    print "Need command"
    print usage
    exit(1)

import subprocess
import re
import xmltodict
from datetime import datetime


def getProcs(procs):
    pid_list = []
    #print "procs:",procs
    if isinstance(procs,list):
        for proc in procs:
            pid_list.append(proc["pid"])
    else:
        pid_list.append(procs["pid"])
    return pid_list


# Replace in proc_list PIDs with used_memory values for corresponding pids.
# Return comma-separated string with used_memory values.
def getProcMemory(procs,proc_list):
    if isinstance(procs,list):
        for proc in procs:
            pid = proc["pid"]
            for i in xrange(len(proc_list)):
                # print "column",proc_list[i],"vs",pid
                if pid == proc_list[i]:
                    proc_list[i] = proc["used_memory"]+"("+pid+")"
        return ",".join(proc_list)
    else:
        return procs["used_memory"]


def memoryJoin(procs):
    s = ""
    for proc in procs:
        s += proc + " Used Memory,"
    # Remove last comma
    return s[:-1]

header_printed = False

def XML2string(block):
    global header_printed
    dom = xmltodict.parse(block)
    procs = getProcs(dom["nvidia_smi_log"]["gpu"]["processes"]["process_info"])
    if not header_printed:
        print "time nvsmi,time python,gpu,PCI sent,PCI recv,GPU util,Memory util,"+memoryJoin(procs)
        header_printed = True
    line = ""
    #print  "Parsed",json.dumps(dom, indent=4)
    #print dom["nvidia_smi_log"]["timestamp"]
    line += dom["nvidia_smi_log"]["timestamp"]
    line += "," + str(datetime.now())
    gpu = dom["nvidia_smi_log"]["gpu"]
    line += ","+gpu["product_name"]
    line += ","+gpu["pci"]["tx_util"]
    line += ","+gpu["pci"]["rx_util"]
    line += ","+gpu["utilization"]["gpu_util"]
    line += ","+gpu["utilization"]["memory_util"]
    line += ","+getProcMemory(gpu["processes"]["process_info"],procs)
    print line
    #return str

list_com = args.command + options
print datetime.now()
print "Executing:",list_com


proc = subprocess.Popen(list_com, stdout=subprocess.PIPE)
block = ""
while True:
    output = proc.stdout.readline()
    if output == '':
        exit_code = proc.poll()
        if exit_code is not None:
            if len(block) > 0:
                XML2string(block)
            exit(exit_code)
    elif re.search("^<\?xml",output):
        # New YAML block
        if len(block) > 1:
            XML2string(block)
            block=""
    else:
        block = block + output
        #print parsed

print "reached unreachable"


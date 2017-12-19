#!/usr/bin/env python

import subprocess
import re

print "v.43"

# Execute file and display output
def execute(file_command, start, stop, ignore, search_pattern):
    print file_command


kernels_start = re.compile("Profiling result:", re.IGNORECASE)
kernels_stop = re.compile("API calls:", re.IGNORECASE)
exclude_pattern = re.compile("^(\s*)(Time|Type)", re.IGNORECASE)
search_pattern = re.compile(r"\S+")
float_pattern = re.compile(r"[0-9\.]+")
delete_pattern = re.compile(r"[a-z\s]+:", re.IGNORECASE)

kernels = []
threshold = 1


#command = "nvprof python tf_cnn_benchmarks.py --num_gpus=1 --batch_size=32 --model=resnet50 --num_batches=3 --num_warmup_batches=1"
command = "nvprof python tf_cnn_benchmarks.py --num_gpus=1 --batch_size=32 --model=resnet50 --num_batches=3 --num_warmup_batches=1"
command_split = str.split(command)

p = subprocess.Popen(command_split, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
analyse = False
while p.poll() is None:
    #print p.stdout.readline(),
    #print "e: ", p.stderr.readline(),
    #for s in p.stderr.readline():
    s, serr = p.communicate()
    #print ":",s,":"
    #print "e:",serr,":e"
    for s in serr.splitlines():
        if analyse:
            if exclude_pattern.search(s) is None:
                s = delete_pattern.sub("",s)
                m = search_pattern.findall(s)
                if len(m) > 0:
                    print s
                    n = len(m)
                    print "Matched groups:",n
                    if n > 6:
                        num = float_pattern.findall(m[0])
                        if len(num) > 0:
                            val = float(num[0])
                            print val,m[6]
                            if val > threshold:
                                kernels.append(m[6])
                        else:
                            print "Matched group %s has no numbers" % (m[0])
                else:
                    print "no matches at", s
        if kernels_start.search(s):
            print "Found start pattern"
            analyse = True
        if kernels_stop.search(s):
            print "Found stop pattern"
            analyse = False


print "Found kernels:", kernels




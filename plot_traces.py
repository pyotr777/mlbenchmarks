#!/usr/bin/env python

# Plot time series with data flot trace files in CSV format

import re
import numpy as np
import csv
import os.path

print "v.01"

trace_dir = "Tensorflow-HP"
filename1 = "nvidia-smi-tfhp.csv"
filename2 = "nvprof-trace-tfhp.scv"
# trace_dir = "HPCG"
# filename1 = "nvidia-smi-hpcg.csv"
# filename2 = "nvprof-trace-hpcg.scv"

file1 = os.path.join(trace_dir,filename1)
file2 = os.path.join(trace_dir,filename2)

print "Reading",file1,file2

# Reading nvprof trace
filename = file2
ignore_pattern = re.compile("\"Start")
include_pattern = re.compile("\[CUDA .*\]")
name_field_index = 18

# Class object for information about series (E.g. "CUDA memcpy HtoD Pageble Device")
class Series:
    name = ""
    timestamps = []
    values = []

    def __init__(self, name):
        self.name = name

series = {}

with open(filename, "rb") as csvfile:
    reader = csv.reader(csvfile)
    for line in reader:
        if len(line) > 3:
            if ignore_pattern.search(line[0]) is None:
                if include_pattern.search(line[name_field_index]) is not None:
                    print line

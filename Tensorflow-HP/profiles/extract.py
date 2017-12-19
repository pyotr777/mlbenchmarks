#!/usr/local/env python

# Extract average values from nvprof log files

import re
import numpy as np
import csv

print "v.03"

filename = "computeBOffsetsKernel_dram.log"

print "Reading",filename

avg_value = "([0-9\.]+)[\)\%]+$"
avg_value_giga = "([0-9\.]+)GB/s$"
avg_value_mega = "([0-9\.]+)MB/s$"
avg_value_kilo = "([0-9\.]+)KB/s$"
avg_value_ = "([0-9\.]+)B/s$"

patterns = [re.compile(avg_value), re.compile(avg_value_giga), re.compile(avg_value_mega), re.compile(avg_value_kilo), re.compile(avg_value_)]
dividers = [1, 1, 1E+3, 1E+6, 1E+9]

ignore_pattern = re.compile("Device")

metrics = []   # picked from colimn 4
picked_values=[]  # avg values picked from column 8

with open(filename, "rb") as csvfile:
    reader = csv.reader(csvfile)
    for line in reader:
        #print line, len(line)
        if len(line) >=8:
            if ignore_pattern.search(line[0]) is None:
                metric = line[3]
                avg_value = line[7]
                print metric, avg_value
                metrics.append(metric)
                #picked_values.append(avg_value)

                for m, pattern in enumerate(patterns):
                    match = pattern.findall(avg_value)
                    if len(match) > 0 :
                        print match[0],
                        if (dividers[m] != 1):
                            print "/",dividers[m]
                        else:
                            print ""
                        picked_values.append(float(match[0]) / float(dividers[m]))
                        break

print picked_values
a = np.array(picked_values, dtype=float)
print np.average(a)


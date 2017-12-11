#!/usr/local/env python

# Extract average values from nvprof log files

import re
import numpy as np

file = "M60_dram_flop.log"
metric = "flop_sp_efficiency"


avg_value = "([0-9\.]+)[\)\%]+$"
avg_value_giga = "([0-9\.]+)GB/s$"
avg_value_mega = "([0-9\.]+)MB/s$"
avg_value_kilo = "([0-9\.]+)KB/s$"
avg_value_ = "([0-9\.]+)B/s$"

patterns = [re.compile(avg_value), re.compile(avg_value_giga), re.compile(avg_value_mega), re.compile(avg_value_kilo), re.compile(avg_value_)]
multiplayers = [1, 1, 1E+3, 1E+6, 1E+9]

pattern = re.compile(metric)
picked_values=[]

for i, line in enumerate(open(file)):
    match = pattern.search(line)
    if match:
        print line
        for m, pattern2 in enumerate(patterns):
            match2 = pattern2.findall(line)
            if len(match2) > 0 :
                print match2[0], multiplayers[m]
                picked_values.append(float(match2[0]) / float(multiplayers[m]))
                break

print picked_values
a = np.array(picked_values, dtype=float)
print np.average(a)


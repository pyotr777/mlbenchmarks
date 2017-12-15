#!/usr/bin/env python

import csv
import re

print "v.46"

def parseKernaleName(name):
    end = name.find("<")
    if end >=0:
        name = name[:end]
    start = name.rfind(":")
    if start >=0:
        start += 1
        name = name[start:]
    start = name.rfind(" ")
    if start >=0:
        start += 1
        name = name[start:]
    return name

activation_pattern = re.compile("GPU activities", re.IGNORECASE)

kernels = []
threshold = 4

filename = "nvprof.log"

with open(filename, "rb") as csvfile:
    reader = csv.reader(csvfile)
    for line in reader:
        if activation_pattern.match(line[0]):
            #print line
            val = float(line[1])
            name = line[7]
            #print val,name
            if val > threshold:
                parsed = parseKernaleName(name)
                if parsed not in kernels:
                    kernels.append(parsed)


#         if analyse:
#             if exclude_pattern.search(s) is None:
#                 s = delete_pattern.sub("",s)
#                 m = search_pattern.findall(s)
#                 if len(m) > 0:
#                     print s
#                     n = len(m)
#                     print "Matched groups:",n
#                     if n > 6:
#                         num = float_pattern.findall(m[0])
#                         if len(num) > 0:
#                             val = float(num[0])
#                             print val,m[6]
#                             if val > threshold:
#                                 kernels.append(m[6])
#                         else:
#                             print "Matched group %s has no numbers" % (m[0])
#                 else:
#                     print "no matches at", s
#         if kernels_start.search(s):
#             print "Found start pattern"
#             analyse = True
#         if kernels_stop.search(s):
#             print "Found stop pattern"
#             analyse = False


print "Found kernels:", kernels




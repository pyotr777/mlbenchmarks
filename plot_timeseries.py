#!/usr/bin/env python

import matplotlib.pyplot as plt

import sys
import numpy as np
import datetime

import plotly.plotly as py
import plotly.tools as tls


if len(sys.argv) < 1:
    print "Need TSV file"
    exit(1)

file = sys.argv[1]
print "Read from",file
data = np.loadtxt(file,delimiter="\t",usecols=(5,4),
    dtype=[('col1','datetime64[s]'),('col2','f8')])

print type(data)        #- numpy.ndarray
print type(data[1][0])  #- numpy.datatime64
x = data[0]
y = data[1]
print x
print y

plt.plot(data)
plt.tight_layout()

plt.savefig("foo.png")


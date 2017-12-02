#!/usr/bin/env python

import matplotlib.pyplot as plt

import sys
import numpy as np
import datetime
import matplotlib.dates as mdates

img_name="prices.pdf"

if len(sys.argv) < 1:
    print "Need TSV file"
    exit(1)

file = sys.argv[1]
print "Read from",file
data = np.loadtxt(file, delimiter="\t", usecols=(5,4,1), dtype=object,
                   converters={5: lambda x: datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%fZ"),
                      			4: np.float})

z = data[:,2]
colors=["r-","g-","b-","y-"]
regions = np.unique(z)
color_counter=0
plt.close('all')
plt.interactive(False)
fig, ax = plt.subplots(1)
fig.autofmt_xdate()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m/%dT%H:%M'))

now = datetime.datetime.now()
now = mdates.date2num(now)
for region in regions:
    print region
    subarray=data[data[:,2] == region]
    #print subarray
    x = mdates.date2num(subarray[:,0])
    x = np.append(now, x)
    y = subarray[:,1]
    y =np.append(y[0],y)
    print y[0]
    ax.plot_date(x,y,fmt=colors[color_counter],
                  drawstyle="steps-pre",linewidth=0.5)
    color_counter+=1
ax.grid() 
plt.savefig(img_name)

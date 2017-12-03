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

tsv_file = sys.argv[1]

if len(sys.argv) > 1:
    img_name=sys.argv[2]

if len(sys.argv) > 2:
    inst_type=sys.argv[3]
else:
    inst_type=tsv_file

print "Read from",tsv_file
data = np.loadtxt(tsv_file, delimiter="\t", usecols=(5,4,1), dtype=object,
                   converters={5: lambda x: datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%fZ"),
                      			4: np.float})

z = data[:,2]
colors=["#ff2200","#dd9900","#ccdd11","#66dd11","#00cc88","#0099cc"]
regions = np.unique(z)
color_counter=0
plt.close('all')
plt.interactive(False)
fig, ax = plt.subplots(1)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %H:%M'))

now = datetime.datetime.now()
now = mdates.date2num(now)
for region in regions:
    print region
    subarray=data[data[:,2] == region]
    #print subarray
    x = mdates.date2num(subarray[:,0])
    x = np.append(now, x)
    y = subarray[:,1]
    print y[0]
    y =np.append(y[0],y)
    ax.plot_date(x,y,fmt=colors[color_counter],
                  drawstyle="steps-pre",label=region,linewidth=0.5)
    color_counter+=1
    
    if color_counter >= len(colors):
        color_counter = 0

mn = np.floor(min(data[:,1]))
mx = np.ceil(max(data[:,1]))
maxticks = 40
arr = np.arange(mn, mx, 0.05)
if len(arr) > maxticks:
    arr = np.arange(mn, mx, 0.1)
if len(arr) > maxticks:
    arr = np.arange(mn, mx, 0.2)

plt.yticks(arr)
ax.grid(color="#ccddee",linewidth=0.3,linestyle="dotted") 
ax.tick_params(axis="x", labelsize=5, rotation=60)
ax.tick_params(axis="y",labelsize=5)
#ax.yaxis.set_label_position("right")
ax.yaxis.tick_right()
ax.legend()
plt.title(inst_type)
plt.savefig(img_name)

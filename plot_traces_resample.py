#!/usr/bin/env python

# Plot time series with data flot trace files in CSV format

import re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import csv
import os.path
import datetime
from cycler import cycler
import pandas as pd
import matplotlib.ticker as ticker

print "v.0.90"

trace_dir = "Tensorflow-HP"
filename1 = "nvidia-smi-tfhp.csv"
filename2 = "nvprof-trace-tfhp.csv"
# trace_dir = "HPCG"
# filename1 = "nvidia-smi-hpcg.csv"
# filename2 = "nvprof-trace-hpcg.csv"

img_name = trace_dir

maxrows = 5000
subplots = 5

# Class object for information about series (E.g. "CUDA memcpy HtoD Pageble Device")
# Name and index are defined on an instance creation (in __init__ function),
# timestamp and value are filled later.
class extDataFrame(pd.DataFrame):
    name = ""
    csv_index = 0 # column index
    subplot = 1 # subplot number
    axis = 1 # Y-axis number (1 or 2)

    def __init__(self, name, columns, subplot = 1, index = 0, axis = 1):
        self.name = name
        self.subplot = subplot
        self.csv_index = index
        self.axis = axis
        super(extDataFrame,self).__init__(columns=columns)

    def __str__(self):
        s = "DataFrame "+self.name+"\n"
        s = s+ super(extDataFrame,self).__str__()+"\n"
        return s


# Search dataframes list.
# Returns existing element if name is found,
# a new element appended to the list otherwise.
def getDataframe(name, subplot = 1):
    global dataframes
    for df in dataframes:
        if df.name == name:
            return df
    df_n = extDataFrame(name,["Throughput"],subplot = subplot)
    print "Dataframe "+name+" created."
    dataframes.append(df_n)
    return df_n


# Save current plot to a file
def saveFig(img_name):
    print "saveing to "+ img_name
    plt.savefig(img_name, bbox_inches='tight')


file1 = os.path.join(trace_dir,filename1)
file2 = os.path.join(trace_dir,filename2)


# Reading nvprof trace

filename = file2
print "Reading",filename
title_pattern = re.compile("^(Start|s).*")
cuda_pattern = re.compile("\[CUDA .*\]")
# Column indexes
# nvprof trace file
name_field_index = 18
time_field_index = 0
duration_field_index = 1
SSMem_field_index = 9
DSMem_field_index = 10
size_field_index = 11
throughput_field_index = 12
src_field_index = 13
dst_field_index = 14
context_index = 16
stream_index = 17

dataframes = [] # Array of DataFrames class instances
rowcounter = 1
with open(filename, "rb") as csvfile:
    reader = csv.reader(csvfile)
    for line in reader:
        if rowcounter > maxrows:
            break

        if len(line) > 3:
            if title_pattern.search(line[0]) is None:
                if cuda_pattern.search(line[name_field_index]) is not None:
                    name = line[name_field_index]+" "+line[src_field_index] +line[dst_field_index]
                    name = name.replace("CUDA memcpy ","")
                    name = name.replace("CUDA ","")
                    subplot = 1
                    if line[name_field_index].find("DtoD") > 0 or line[name_field_index].find("memset") > 0:
                        subplot = 2
                    df = getDataframe(name, subplot = subplot)
                    start = pd.to_datetime(line[0], unit='s')
                    df.loc[start] = float(line[throughput_field_index])

            rowcounter += 1
    csvfile.close()

print "nvprof array length", len(dataframes)
print "dataframes:"
for df in dataframes:
    print df.name,df.shape

colors=["#5988c7","#e3a94d","#8db763","#7aced4","#8e92ea","#ce63a1"]

# Concatenate array of dataframes into several dataframe - one for each subplot.
# Throughput column of each dataframe will be distinct column in the new dataframe.
dataframe_con = []
...
dataframe_con[dataframes.subplot] = dataframes[0]['Throughput']
max_ =  dataframe.max()
column_names = [dataframes[0].name + " "+ str(max_)]
for df in dataframes[1:]:
    max_ = df['Throughput'].max()
    column_names.append(df.name + " "+ str(max_))
    df = df['Throughput']
    
    dataframe = pd.concat([dataframe,df], axis=1)

dataframe.columns = column_names

plt.interactive(False)
#plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = 20,15

# Plot BOX chart
fig, axis = plt.subplots(1)

axis.set_title("nvprof "+trace_dir)
# Box plot for nvprof dataframes
dataframe.plot.box(logy=True,rot=45, ax = axis)
axis.yaxis.grid(color="#e0e0e0", linestyle=":",linewidth=0.5)
saveFig(img_name+"_box.pdf")


# Plot LINE charts
plot_resampled = False
fig, axarr = plt.subplots(2) #, sharex = True)
axarr[0].set_title("nvprof "+trace_dir)
for df in dataframes:
    axis = axarr[df.subplot-1]
    x = np.array(df.index, dtype = float)
    y = np.array(df.loc[:,'Throughput'], dtype = float)
    #print x,y
    axis.plot(x,y,alpha=0.9,label=df.name) #,drawstyle="steps-post")
    
    if (plot_resampled):
        resampled = df.resample("500ms").max()
        x = np.array(resampled.index, dtype = float)
        y = np.array(resampled.iloc[:,0], dtype = float)
        #print x,y
        axis.plot(x,y,alpha=0.5,label=df.name+"_res",linestyle="--")
        

for axis in axarr:
    axis.legend()
    axis.xaxis.grid(color="#e0e0e0", linestyle=":",linewidth=0.5)
    axis.xaxis.set_major_locator(plt.MaxNLocator(24))
axarr[0].set_yscale('log')
axarr[1].set_yscale('log')
saveFig(img_name+"_nvprof.pdf")

# Plot BAR chart
fig, axes = plt.subplots(2, sharex = True)
resampled = dataframe.resample("200ms").max()
resampled = resampled.fillna(0)
axis = axes[0]
resampled.plot.bar(stacked=True, ax = axis) #,logy=True) log scale causes distortions on stacked bar.
#ax = plt.gca()
axis.yaxis.grid(color="#e0e0e0", linestyle=":",linewidth=0.5)

ticklabels = ['']*len(resampled.index)
ticklabels[::2] = [item.strftime('%M:%S.%f') for item in resampled.index[::2]]
axis.xaxis.set_major_formatter(ticker.FixedFormatter(ticklabels))
plt.gcf().autofmt_xdate()

saveFig(img_name+"_bar.pdf")

start = 0
# Parse date from readable format to seconds
def parseTime(date_time):
    global start
    dt_obj = datetime.datetime.strptime(date_time, "%Y/%m/%d %H:%M:%S.%f")
    seconds = 0
    if start == 0:
        start = dt_obj
    else:
        seconds = (dt_obj - start).total_seconds()
    return seconds

pat = re.compile("[0-9\.]+")
# Extract float number from a string
def parseFloat(str):
    global pat
    f = pat.search(str)
    if f is not None:
        d = float(f.group())
        return d
    return None


# Reading nvidia-smi trace
# File must be of the following format:
#   first line - column titles,
#   first column - timestamps.

filename = file1
print "Reading",filename

smi_data = pd.read_csv(filename)

#smi_data = smi_data[['Start','Throughput','SrcMemType','DstMemType']]
smi_data.index = pd.to_datetime(smi_data.index, format = "%Y/%m/%d %H:%M:%S.%f")

columns = range(2,8)
print columns
for column in columns:
    smi_data[smi_data.columns[column]] = smi_data[smi_data.columns[column]].apply(parseFloat)

fig, axarr = plt.subplots(3)
sub = smi_data.iloc[:,[2,3]]

axis = axarr[0]
sub.plot(ax = axis)
axis.set_title("nvidia-smi "+trace_dir)

axis.yaxis.grid(color="#e0e0e0", linestyle=":",linewidth=0.5)
axis.xaxis.grid(color="#e0e0e0", linestyle=":",linewidth=0.5)
axis.xaxis.set_major_locator(plt.MaxNLocator(24))

saveFig(img_name+"_smi.pdf")



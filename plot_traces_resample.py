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

print "v.0.70"

trace_dir = "Tensorflow-HP"
filename1 = "nvidia-smi-tfhp.csv"
filename2 = "nvprof-trace-tfhp.csv"
# trace_dir = "HPCG"
# filename1 = "nvidia-smi-hpcg.csv"
# filename2 = "nvprof-trace-hpcg.csv"

img_name = trace_dir+".pdf"

maxrows = 500
subplots = 6

# Class object for information about series (E.g. "CUDA memcpy HtoD Pageble Device")
# Name and index are defined on an instance creation (in __init__ function),
# timestamp and value are filled later.
class extDataFrame(pd.DataFrame):
    name = ""
    index = 0 # column index
    subplot = 1 # subplot number
    axis = 1 # Y-axis number (1 or 2)

    def __init__(self, name, columns, index = 0, subplot = 1, axis = 1):
        self.name = name
        self.index = index
        self.subplot = subplot
        self.axis = axis
        super(extDataFrame,self).__init__(columns=columns)

    def __str__(self):
        s = "DataFrame "+self.name+"\n"
        s = s+ super(extDataFrame,self).__str__()+"\n"
        return s

# Search dataframes list.
# Returns existing element if name is found,
# a new element appended to the list otherwise.
def getDataframe(name):
    global dataframes
    for df in dataframes:
        if df.name == name:
            return df
    df_n = extDataFrame(name,["Throughput"])
    dataframes.append(df_n)
    return df_n


file1 = os.path.join(trace_dir,filename1)
file2 = os.path.join(trace_dir,filename2)
print "Reading",file1,file2


# Reading nvprof trace

filename = file2
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
                    #print line
                    name = line[name_field_index]+" "+line[src_field_index] +line[dst_field_index]
                    name = name.replace("CUDA memcpy ","")
                    name = name.replace("CUDA ","")
                    df = getDataframe(name)
                    start = pd.to_datetime(line[0], unit='s')
                    # Do not store size and duration
                    #print float(line[throughput_field_index])
                    df.loc[start] = [float(line[throughput_field_index])]
        rowcounter += 1
    csvfile.close()

print "nvprof array length", len(dataframes)
print "dataframes:"
for df in dataframes:
    print df.name


# colors=[["#f9ea62","#ce8900","#ffad74","#ff9015","#ff5000","#95361d"],
#     ["#9fe0b6","#00ae42","#cde67e","#20d2c4","#00aac7","#0055bb"]]
#colors=["#f9ea62","#ce8900","#ffad74","#ff9015","#ff5000","#95361d"]
colors=["#39a6f4","#fdb94c","#49dd4c","#6bd5de","#f78ae6","#ff5000"]

# Concatenate array of dataframes into one dataframe
dataframe = []
dataframe = dataframes[0]['Throughput']
max_ =  dataframe.max()
column_names = [dataframes[0].name + " "+ str(max_)]
for df in dataframes[1:]:
    print df['Throughput'].max()
    max_ = df['Throughput'].max()
    column_names.append(df.name + " "+ str(max_))
    df = df['Throughput']
    
    dataframe = pd.concat([dataframe,df], axis=1)

dataframe.columns = column_names

plt.interactive(False)
#plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = 15,10

fig, axarr = plt.subplots(subplots,sharex=True)
#fig.subplots_adjust(hspace=0)
axarr[0].set_title("nvprof "+trace_dir)

# Box plot for nvprof dataframes
dataframe.plot.box(logy=True,rot=45)


for df in dataframes:
    sum_ms = df.Throughput.resample("1000ms").sum()
    print sum_ms.shape
    #axarr.scatter(x,y,s=0.5,alpha=0.5,label=series.name)
    #axarr.plot(x,y,linewidth=0.5,alpha=0.5,label=series.name)
    if sum_ms.name.find("Dynamic") > 0:
        axis = rightax
    else:
        axis = axarr[sum_ms.subplot-1]

    # TODO:
    axis.plot(x,y,w,alpha=0.9,label=series.name)


for axis in axarr:
    axis.legend()
    axis.xaxis.grid(color="#e0e0e0", linestyle="--",linewidth=0.5)
    axis.xaxis.set_major_locator(plt.MaxNLocator(24))

right_legend = rightax.legend(loc = 'upper left', bbox_to_anchor=(1.02,1))
art.append(right_legend)

# Creates an array of Series instances
def parseSeriesNames(line):
    skip_columns = 2 # Skip first 2 columns
    columns = line[skip_columns:]
    print columns
    series = [None for i in range(len(columns))]
    for i,title in enumerate(columns):
        series[i] = Series(title,i+skip_columns)
    return series

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
series_arr2 = []
time_field_index = 0

with open(filename, "rb") as csvfile:
    reader = csv.reader(csvfile)
    titles = reader.next()
    series_arr2 = parseSeriesNames(titles) # array of instances of class Series
    rowcounter=1
    for line in reader:
        timestamp = parseTime(line[time_field_index])
        for series in series_arr2:
            series.timestamps.append(timestamp)
            series.values.append(parseFloat(line[series.index]))
            series.subplot = 4
            if series.name.find("utilization") >= 0:
                series.subplot = 5
            elif series.name.find("clocks") >= 0:
                series.subplot = 6
        if rowcounter > maxrows:
            break
        rowcounter += 1

    csvfile.close()

print "nvidia-smi array length", len(series_arr2)
for series in series_arr2:
    x = np.array(series.timestamps, dtype = float)
    y = np.array(series.values, dtype = float)
    axis = axarr[series.subplot-1]
    axis.plot(x,y,alpha=0.9,label=series.name)

axarr[3].set_title("nvidia-smi "+trace_dir)

for axis in axarr:
    axis.legend()


plt.savefig(img_name, bbox_extra_artists=art, bbox_inches='tight')



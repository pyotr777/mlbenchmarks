#!/usr/bin/env python

# Plot time series with data flot trace files in CSV format

import re
import numpy as np
import matplotlib.pyplot as plt
import csv
import os.path
import datetime
from cycler import cycler

print "v.0.57"

min_duration = 0.0002
maxrows = 500000
subplots = 6

# Class object for information about series (E.g. "CUDA memcpy HtoD Pageble Device")
# Name and index are defined on an instance creation (in __init__ function),
# timestamp and value are filled later.
class Series:
    name = ""
    timestamps = []
    durations = []
    values = []
    index = 0   # column index
    subplot = 1 # Subplot number

    def __init__(self, name, index = 0):
        self.name = name
        self.index = index
        self.values = []
        self.timestamps = []
        self.durations = []
        subplot = 1

    def fill(self,timestamp, duration, value):
        self.timestamps.append(timestamp)
        if duration < min_duration:
            duration = min_duration
        self.durations.append(duration)
        self.values.append(value)

    def printme(self):
        print "name=",self.name,"length",len(self.timestamps),"plot",self.subplot
        # for i, val in enumerate(self.timestamps):
        #     print self.timestamps[i],self.values[i]


# Returns existing array member if name exists,
# or a new instance otherwise.
def getSeriesByName(series_arr, name, index):
    for series in series_arr:
        if series.name == name:
            return series
    #print "Add new series ",name
    series_arr.append(Series(name, index))
    return series_arr[-1]


# Returns an array of Series class instances,
# where for existing names existing instances are used,
# and for new names new instances are created.
def getSeriesArray(series_arr, names, indexes, subplots):
    new_series = []
    for i, val in enumerate(names):
        series = getSeriesByName(series_arr,names[i], indexes[i])
        series.subplot = subplots[i]
        new_series.append(series)
    return new_series

# Returns an array of Series class instances
# from series_arr if instance with the same name exitst,
# new instance otherwise.
# Uses global variables for column indexes.
def getCudaSeries(series_arr, line):
    base_name = line[name_field_index]+" "+line[src_field_index] +line[dst_field_index]
    names = [ base_name + " Throughput(GB/s)"]
    col_indexes = [throughput_field_index]
    subplots = [1]
    if line[name_field_index].find("DtoD") > 0 or line[name_field_index].find("memset") > 0:
        subplots = [2]
    return getSeriesArray(series_arr,names,col_indexes, subplots)


# Returns an array of Series class instances
# from series_arr if instance with the same name exitst,
# new instance otherwise.
# Uses global variables for column indexes.
def getKernelSeries(series_arr, line):
    base_name = "Stream" + line[stream_index] # Put all kernels in one series
    names = [base_name + " Static SMem(KB)", base_name + " Dynamic SMem(B)"]
    col_indexes = [SSMem_field_index, DSMem_field_index]
    subplots = [3,3]
    return getSeriesArray(series_arr,names,col_indexes, subplots)

# Save data from CSV file record
# to Series class instance.
def fillSeries(series, line):
    # print series.name,line[time_field_index],line[series.index]
    series.fill(line[time_field_index],float(line[duration_field_index])/1000,line[series.index])


trace_dir = "Tensorflow-HP"
filename1 = "nvidia-smi-tfhp.csv"
filename2 = "nvprof-trace-tfhp.csv"
# trace_dir = "HPCG"
# filename1 = "nvidia-smi-hpcg.csv"
# filename2 = "nvprof-trace-hpcg.csv"

file1 = os.path.join(trace_dir,filename1)
file2 = os.path.join(trace_dir,filename2)

print "Reading",file1,file2



series_arr1 = [] # Array of Series class instances


# Reading nvprof trace
filename = file2
ignore_pattern = re.compile("^[a-zA-z]+")
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


rowcounter = 1

with open(filename, "rb") as csvfile:
    reader = csv.reader(csvfile)
    for line in reader:
        if rowcounter > maxrows:
            # print len(series_arr1)
            for series in series_arr1:
                series.printme()
            break
        if len(line) > 3:
            if ignore_pattern.search(line[0]) is None:
                if cuda_pattern.search(line[name_field_index]) is not None:
                    # print line
                    # Get a new or existing instance of class Series
                    series_arr = getCudaSeries(series_arr1,line)
                else:
                    series_arr = getKernelSeries(series_arr1,line)
                # Fill series instance with corresponding fields of the CSV file line
                for series in series_arr:
                    fillSeries(series, line)
                    #print "Filled series",series.name
                    #series.printme()
        rowcounter += 1
    csvfile.close()

print "nvprof array length", len(series_arr1)
# print series_arr1

img_name = trace_dir+".pdf"

plt.interactive(False)
#plt.style.use('ggplot')
# Set figure width to 12 and height to 9
fig_size = plt.rcParams["figure.figsize"]
fig_size[0] = 15
fig_size[1] = 10
plt.rcParams["figure.figsize"] = fig_size

fig, axarr = plt.subplots(subplots,sharex=True)
#fig.subplots_adjust(hspace=0)
axarr[0].set_title("nvprof "+trace_dir)

# colors=[["#f9ea62","#ce8900","#ffad74","#ff9015","#ff5000","#95361d"],
#     ["#9fe0b6","#00ae42","#cde67e","#20d2c4","#00aac7","#0055bb"]]
#colors=["#f9ea62","#ce8900","#ffad74","#ff9015","#ff5000","#95361d"]
colors=["#39a6f4","#fdb94c","#49dd4c","#6bd5de","#f78ae6","#ff5000"]
art = []

rightax = axarr[2].twinx()
rightax.set_prop_cycle(cycler('color',colors))

for series in series_arr1:
    x = np.array(series.timestamps, dtype = float)
    y = np.array(series.values, dtype = float)
    w = np.array(series.durations, dtype = float)
    #print series.name,x,y, w
    #axarr.scatter(x,y,s=0.5,alpha=0.5,label=series.name)
    #axarr.plot(x,y,linewidth=0.5,alpha=0.5,label=series.name)
    if series.name.find("Dynamic") > 0:
        axis = rightax
    else:
        axis = axarr[series.subplot-1]
    axis.bar(x,y,w,alpha=0.9,label=series.name)


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



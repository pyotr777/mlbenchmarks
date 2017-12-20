#!/usr/bin/env python

# Plot time series with data flot trace files in CSV format

import re
import numpy as np
import matplotlib.pyplot as plt
import csv
import os.path
#import sys

print "v.37"

min_duration = 0.0002
maxrows = 10000


# Class object for information about series (E.g. "CUDA memcpy HtoD Pageble Device")
# Name and index are defined on an instance creation (in __init__ function),
# timestamp and value are filled later.
class Series:
    name = ""
    timestamps = []
    durations = []
    values = []
    index = 0   # column index
    axis = 1    # Plot axis (1 or 2)
    subplot = 1 # Subplot number (1 or 2)

    def __init__(self, name, index = 0):
        self.name = name
        self.index = index
        self.values = []
        self.timestamps = []
        self.durations = []
        axis = 1
        subplot = 1

    def fill(self,timestamp, duration, value):
        self.timestamps.append(timestamp)
        if duration < min_duration:
            duration = min_duration
        self.durations.append(duration)
        self.values.append(value)

    def printme(self):
        print "name=",self.name,"length",len(self.timestamps),"plot",self.subplot,"axis",self.axis
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
def getSeriesArray(series_arr, names, indexes, axes, subplots):
    new_series = []
    for i, val in enumerate(names):
        series = getSeriesByName(series_arr,names[i], indexes[i])
        series.axis = axes[i]
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
    axes = [1]
    if line[name_field_index].find("DtoD") > 0:
        axes = [2]
    subplots = [1]
    return getSeriesArray(series_arr,names,col_indexes, axes, subplots)


# Returns an array of Series class instances
# from series_arr if instance with the same name exitst,
# new instance otherwise.
# Uses global variables for column indexes.
def getKernelSeries(series_arr, line):
    base_name = "Stream" + line[stream_index] # Put all kernels in one series
    names = [base_name + " Static SMem(KB)", base_name + " Dynamic SMem(B)"]
    col_indexes = [SSMem_field_index, DSMem_field_index]
    axes = [1,2]
    subplots = [2,2]
    return getSeriesArray(series_arr,names,col_indexes, axes, subplots)

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
            csvfile.close()
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

print "CUDA array length", len(series_arr1)
# print series_arr1

img_name = trace_dir+".pdf"

plt.interactive(False)
#plt.style.use('ggplot')
# Set figure width to 12 and height to 9
fig_size = plt.rcParams["figure.figsize"]
fig_size[0] = 15
fig_size[1] = 10
plt.rcParams["figure.figsize"] = fig_size
fig = plt.figure()
ax11 = fig.add_subplot(311)
ax11.set_title("nvprof "+trace_dir + " memory throughput")
ax12 = ax11.twinx()
ax21 = fig.add_subplot(312)
ax22 = ax21.twinx()
ax21.set_title("nvprof "+trace_dir + " Shared memory")
colors=[["#f9ea62","#ce8900","#ffad74","#ff9015","#ff5000","#95361d"],
    ["#9fe0b6","#00ae42","#cde67e","#20d2c4","#00aac7","#0055bb"]]
color_index = [0,0]
for series in series_arr1:
    x = np.array(series.timestamps, dtype = float)
    y = np.array(series.values, dtype = float)
    w = np.array(series.durations, dtype = float)
    #print series.name,x,y, w
    #ax.scatter(x,y,s=0.5,alpha=0.5,label=series.name)
    #ax.plot(x,y,linewidth=0.5,alpha=0.5,label=series.name)

    if series.subplot == 1:
        if series.axis == 1:
            axis = ax11
            color = colors[0][color_index[0]]
            color_index[0] += 1
            if color_index[0] >= 6:
                color_index[0] = 0
        else:
            axis = ax12
            print color_index[1]
            color = colors[1][color_index[1]]
            color_index[1] += 1
            if color_index[1] >= 6:
                color_index[1] = 0
    else:
        if series.axis == 1:
            axis = ax21
            color = colors[0][color_index[0]]
            color_index[0] += 1
            if color_index[0] >= 6:
                color_index[0] = 0
        else:
            axis = ax22
            color = colors[1][color_index[1]]
            color_index[1] += 1
            if color_index[1] >= 6:
                color_index[1] = 0

    axis.bar(x,y,w,color=color,alpha=0.9,label=series.name)

ax11.legend(loc="upper left")
ax12.legend(loc="upper right")
ax21.legend(loc="upper left")
ax22.legend(loc="upper right")
ax11.set_yscale('log')
ax12.set_yscale('log')
ax21.set_yscale('log')
ax22.set_yscale('log')
plt.savefig(img_name)

# Reading nvidia-smi trace
# File must be of the following format:
#   first line - column titles,
#   first column - timestamps.

# filename = file1
# series_arr2 = []
# time_field_index = 0
# mem_total_field_index = 2
# mem_used_field_index = 3
# gpu_util_field_index = 4
# mem_util_field_index = 4
# SM_clock_field_index = 6

# with open(filename, "rb") as csvfile:
#     reader = csv.reader(csvfile)
#     titles = reader.next()
#     series_arr2 = parseSeriesNames(titles) # array of instances of class Series
#     for line in reader:
#         timestamp = parseTime(line[time_field_index])
#         for series in series_arr2:
#             fillSeries(series,line)

#     csvfile.close()

# plotSeries(series_arr1, series_arr2)






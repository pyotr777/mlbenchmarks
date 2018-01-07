#!/usr/bin/env python

# Plot time series with data flot trace files in CSV format

import re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
#import csv
import os.path
import datetime
from cycler import cycler
import pandas as pd
import matplotlib.ticker as ticker
import sys

print "v.0.95"


trace_dir1 = "Tensorflow-HP" 
trace_dir2 = "HPCG"
#filename1 = "nvidia-smi-tfhp.csv"
filename1 = "nvprof-trace-tfhp.csv"
#filename2 = "nvidia-smi-hpcg.csv"
filename2 = "nvprof-trace-hpcg.csv"

maxrows = None

# nvidia-smi trace format
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
name_field_index = 18

file1 = os.path.join(trace_dir1,filename1)
file2 = os.path.join(trace_dir2,filename2)

print "Reading",file1,file2

columns = [time_field_index, duration_field_index,
           SSMem_field_index, DSMem_field_index,
           size_field_index, throughput_field_index,
           src_field_index, dst_field_index,
           context_index, stream_index,
           name_field_index]


# Save current plot to a file
def saveFig(img_name):
    print "saveing to "+ img_name
    plt.savefig(img_name, bbox_inches='tight')


# Convert unique values in column "FullName" to new columns
def mergeColumnNames(df_org):
    df = df_org.pivot(index = 'Start', columns = 'FullName', 
                         values = 'Throughput')
    df = df.fillna(0)  # Fill empty cells with 0-s
    return df


# Add max values to column names
def appendMaxValues2ColumnNames(df,series):
    cols = len(df.columns)
    col_names = []
    for i in range(0,cols):
        col_names.append(series+df.columns[i]+" " +'{:.3f}'.format(df.iloc[:,i].max()))
    df.columns = col_names
    return df


# Plot BOX plot of DataFrame columns
# and save to an image file
def boxPlotDF( df, imgname):
    # To remove zero values need to split DataFrame into Series (they will have different lengths)
    # Convert columns to Series and add to a list
    # Create list of column names
    x_arr = []
    names = []
    for column in df: 
        x = df[column]
        x = x[x != 0]
        print '{:46.44} {:8.8} '.format(column, x.shape),
        arr = x.values
        print '{:6d}'.format(len(arr)),
        x_arr.append(arr)
        names.append(column)
        print '{:3d}'.format(len(x_arr))

    # BOX plot of memcpy operations
    plt.interactive(False)
    plt.rcParams['figure.figsize'] = 12,8
    fig, axis = plt.subplots(1)
    axis.boxplot(x_arr, 0, '', labels = names)
    plt.xticks(rotation=90)
    #ax = plt.gca()
    #ax.set_yscale("log")
    axis.yaxis.grid(color="#e0e0e0", linestyle=":",linewidth=0.5)
    saveFig(imgname)


# Reading nvprof trace
print file1
df_tf = pd.read_csv(file1, header = 0, usecols = columns, 
                 skiprows=[0,1,2,4], nrows = maxrows)
print df_tf.shape
print file2
df_hpcg = pd.read_csv(file2, header = 0, usecols = columns, 
                 skiprows=[0,1,2,4], nrows = maxrows)
print df_hpcg.shape

# Select columns with memory operations
df_tf_cuda = df_tf.loc[df_tf['Name'].str.contains('\[CUDA')]
df_hpcg_cuda = df_hpcg.loc[df_hpcg['Name'].str.contains('\[CUDA')]

df_tf_cuda['FullName'] = df_tf_cuda['Name'] + " " + df_tf_cuda['SrcMemType']+df_tf_cuda['DstMemType'].fillna("")
df_hpcg_cuda['FullName'] = df_hpcg_cuda['Name'] + " " + df_hpcg_cuda['SrcMemType']+df_hpcg_cuda['DstMemType'].fillna("")

df_tf_throughput = mergeColumnNames(df_tf_cuda)
df_hpcg_throughput = mergeColumnNames(df_hpcg_cuda)

df_tf_throughput = appendMaxValues2ColumnNames(df_tf_throughput,"TF")
df_hpcg_throughput = appendMaxValues2ColumnNames(df_hpcg_throughput,"HPCG")

plt.rcParams['figure.figsize'] = 12,8

# Concatenate columns of two DFs into one DF
df_full = pd.concat([df_tf_throughput,df_hpcg_throughput], axis = 1).fillna(0)

# Remove "memset" columns
df_memcpy = df_full.filter(regex=("^((?!memset).)*$"))
df_DH = df_memcpy.filter(regex=(".*(HtoD|DtoH).*"))

boxPlotDF(df_memcpy, "memcpy_box.pdf")
boxPlotDF(df_DH, "memcpy_DHHD_box.pdf")

sys.exit()






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
#...
dataframe_con[dataframes.subplot] = dataframes[0]['Throughput']
max_ =  dataframe.max()
column_names = [dataframes[0].name + " "+ str(max_)]
for df in dataframes[1:]:
    max_ = df['Throughput'].max()
    column_names.append(df.name + " "+ str(max_))
    df = df['Throughput']
    
    dataframe = pd.concat([dataframe,df], axis=1)

dataframe.columns = column_names


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



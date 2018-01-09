#!/usr/bin/env python

# Plot time series with data flot trace files in CSV format

import re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import os.path
import datetime
from cycler import cycler
import pandas as pd
import matplotlib.ticker as ticker
import sys

print "v.0.102"


trace_dir1 = "Tensorflow-HP" 
trace_dir2 = "HPCG"
filename1 = "nvprof-trace-tfhp.csv"
filename2 = "nvprof-trace-hpcg.csv"
filename_smi_tfhp = "nvidia-smi-tfhp.csv"
filename_smi_hpcg = "nvidia-smi-hpcg.csv"

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
df_DD = df_memcpy.filter(regex=(".*DtoD.*"))

boxPlotDF(df_DD, "memcpy_DD_box.pdf")
boxPlotDF(df_DH, "memcpy_DHHD_box.pdf")


# Plot memory operation profiles
df_DD_TF = df_DD.filter(regex=("^TF.*"))
df_DD_HPCG = df_DD.filter(regex=("^HPCG.*"))

df_DH_TF = df_DH.filter(regex=("^TF.*"))
df_DH_HPCG = df_DH.filter(regex=("^HPCG.*"))

plt.rcParams['figure.figsize'] = 14,12
fig, axarr = plt.subplots(4)
df_DD_TF.plot(drawstyle="steps-post",linewidth=0.5,alpha=0.7,ax = axarr[0])
df_DD_HPCG.plot(drawstyle="steps-post",linewidth=0.5,alpha=0.7,ax = axarr[1])
df_DH_TF.plot(drawstyle="steps-post",linewidth=0.5,alpha=0.7,ax = axarr[2])
df_DH_HPCG.plot(drawstyle="steps-post",linewidth=0.5,alpha=0.7,ax = axarr[3])
for axis in axarr:
    axis.legend()
    axis.xaxis.grid(color="#e0e0e0", linestyle=":",linewidth=0.5)
    axis.xaxis.set_major_locator(plt.MaxNLocator(24))
saveFig("memcpy_graph.pdf")

#sys.exit()



# SMI data

filename1 = os.path.join(trace_dir1, filename_smi_tfhp)
filename2 = os.path.join(trace_dir2, filename_smi_hpcg)
print "Reading",filename1,filename2

# Reading nvidia-smi trace
# File must be of the following format:
#   first line - column titles,
#   first column - timestamps.
smi_tfhp = pd.read_csv(filename1)
smi_hpcg = pd.read_csv(filename2)


# Parse date from readable format to seconds
def parseTime(date_time, start = 0):
    #global start
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



smi_tfhp.index = pd.to_datetime(smi_tfhp['timestamp'])
start = smi_tfhp.index[0]
smi_tfhp["sec"] = smi_tfhp["timestamp"].apply(parseTime, args = (start,))

smi_tfhp = smi_tfhp.set_index(["sec"])
smi_tfhp = smi_tfhp.drop(columns = ['timestamp', ' name'])

smi_tfhp = smi_tfhp.applymap(parseFloat)
smi_tfhp_MB = smi_tfhp.filter(regex=(".*\[MiB.*"))
smi_tfhp_pr = smi_tfhp.filter(regex=(".*\[\%.*"))
smi_tfhp_Hz = smi_tfhp.filter(regex=(".*\[MHz.*"))


smi_hpcg.index = pd.to_datetime(smi_hpcg['timestamp'])
start = smi_hpcg.index[0]
smi_hpcg["sec"] = smi_hpcg["timestamp"].apply(parseTime, args = (start,))

smi_hpcg = smi_hpcg.set_index(["sec"])
smi_hpcg = smi_hpcg.drop(columns = ['timestamp', ' name'])

smi_hpcg = smi_hpcg.applymap(parseFloat)
smi_hpcg_MB = smi_hpcg.filter(regex=(".*\[MiB.*"))
smi_hpcg_pr = smi_hpcg.filter(regex=(".*\[\%.*"))
smi_hpcg_Hz = smi_hpcg.filter(regex=(".*\[MHz.*"))


plt.rcParams['figure.figsize'] = 12,12
fig, axarr = plt.subplots(6)
smi_tfhp_MB.plot(drawstyle="steps-post",linewidth=0.5,alpha=0.9,ax = axarr[0])
axarr[0].set_title("nvidia-smi TF")
smi_hpcg_MB.plot(drawstyle="steps-post",linewidth=0.5,alpha=0.9,ax = axarr[1])
axarr[1].set_title("HPCG")
smi_tfhp_pr.plot(drawstyle="steps-post",linewidth=0.5,alpha=0.9,ax = axarr[2])
axarr[2].set_title("TF")
smi_hpcg_pr.plot(drawstyle="steps-post",linewidth=0.5,alpha=0.9,ax = axarr[3])
axarr[3].set_title("HPCG")
smi_tfhp_Hz.plot(drawstyle="steps-post",linewidth=0.5,alpha=0.9,ax = axarr[4])
axarr[4].set_title("TF")
smi_hpcg_Hz.plot(drawstyle="steps-post",linewidth=0.5,alpha=0.9,ax = axarr[5])
axarr[5].set_title("HPCG")
for axis in axarr:
    axis.legend()
    axis.xaxis.grid(color="#e0e0e0", linestyle=":",linewidth=0.5)
    axis.xaxis.set_major_locator(plt.MaxNLocator(24))
    axis.yaxis.grid(color="#e0e0e0", linestyle=":",linewidth=0.5)



saveFig("nvidia_smi.pdf")



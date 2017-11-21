#!/bin/bash
#location of HPL
HPCG_DIR=`pwd`

usage="$0 <MPI procs>"

PROCS=2  # Default MPI proccesses
if [ $# -ge 1 ]; then
	PROCS=$1
else
	echo "$usage"
fi

echo "Running HPCG for $PROCS MPI processes"

nvcc --version
mpirun --version

HOSTNAME=`hostname`
DATETIME=`hostname`.`date +"%m%d.%H%M%S"`

echo "Results in ./results/xhpcg_x_gpu-$DATETIME-output.txt"
#********************************************************************
# Examples for running with boosted clocks on P100
# Uncomment and modifiy appropriate lines as desired
#********************************************************************

nvidia-smi


#sudo nvidia-smi -pm 1
#sudo nvidia-smi -acp 0

#sudo nvidia-smi -ac 715,1328 # max clocks on P100 PCIe
#sudo nvidia-smi -ac 715,1480 # max clocks on P100 SXM2


#sudo nvidia-smi --auto-boost-default=0          # disable K80/M40 autoboost feature
#sudonvidia-smi -ac 2505,562                    # set K80 base clock
#sudo nvidia-smi -ac 2505,875                         # set K80 base clock

#sudo nvidia-smi -ac 3004,875                        # set K40 max clock

#udo nvidia-smi -ac 3004,949                        # set M40 base clk
#udo nvidia-smi -ac 3004,1114                   # set M40 max clk

# to enable autoboost on K80
#sudo nvidia-smi --auto-boost-default=1         # to enable autoboost on K80

#***********************************

# Note the hpcg.dat file defines the grid size and running time paramters. For an official subimssion you should use the longer (1 hr+) run time. Benchmark result should typically be about same as the shorter (1 min) run time.
cp hpcg.dat_128x128x128_60 hpcg.dat
#cp hpcg.dat_256x256x256_60 hpcg.dat        # 60 sec run
#cp hpcg.dat_256x256x256_3660 hpcg.dat      # 3660 sec run - use for official submission

#export OMP_NUM_THREADS=20
#export OMP_NUM_THREADS=16
export OMP_NUM_THREADS=1
#export CUDA_VISIBLE_DEVICES=2,3

MPIFLAGS="--mca btl tcp,sm,self"   # just to get rid of warning on psg cluster node wo proper IB sw installed

#HPCG_BIN=xhpcg-3.1_gcc_485_cuda90103_ompi_1_10_2_sm_35_sm_50_sm_60_sm_70_ver_8_16_17
HPCG_BIN=xhpcg-3.1_gcc_485_cuda90176_ompi_1_10_2_sm_35_sm_50_sm_60_sm_70_ver_10_8_17

#TAU_SAMPLING=1
export TAU_TRACE=1
echo " ****** running HPCG binary=$HPCG_BIN on $PROCS GPUs with TAU tracing ***************************** "
mpirun -np $PROCS tau_exec $HPCG_DIR/$HPCG_BIN | tee ./results/xhpcg_2_gpu-$DATETIME-output.txt
echo " ****** running HPCG binary=$HPCG_BIN on 4 GPUs ***************************** "
#mpirun -np 4 $MPIFLAGS $HPCG_DIR/$HPCG_BIN | tee ./results/xhpcg_4_gpu-$DATETIME-output.txt
echo " ****** running HPCG binary=$HPCG_BIN on 8 GPUs ***************************** "
#mpirun -np 8 $MPIFLAGS $HPCG_DIR/$HPCG_BIN | tee ./results/xhpcg_8_gpu-$DATETIME-output.txt


grep "final" ./results/xhpcg_2_gpu-$DATETIME-output.txt

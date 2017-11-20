# HPCG benchmark

[www.hpcg-benchmark.org/software/](http://www.hpcg-benchmark.org/software/index.html)

Install and run HPCG benchmark on a remote computer.

## Usage outline

1. Install with ```install.sh``` script.
2. Run with ```run.sh``` script.

## Instructions

### install.sh usage

It will install MPI, NVIDIA drivers and CUDA Toolkit required to run HPCG.
After that the remote computer is restarted and HPCG is installed.

### run.sh usage

Login to the remote computer. 
Define number of GPUs you need to benchmark. 
Run 

```
cd hpcg3.1
./run.sh <GPUs>
```

where GPUs is the number of GPUs to benchmark.




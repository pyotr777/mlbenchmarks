rsync -avr $1 --include="*.log" --exclude="*" ubuntu@ec2-34-228-81-32.compute-1.amazonaws.com:benchmarks/scripts/tf_cnn_benchmarks/ .

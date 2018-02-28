#!/bin/bash

echo "$# arguments, 1=$1"

if [ "$#" -lt 1 ]; then
	echo "Need file with cProfile profile"
	exit 1
fi

python /Users/peterbryzgalov/Library/Python/2.7/lib/python/site-packages/pyprof2calltree.py -k -i $1

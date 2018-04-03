#!/bin/bash
ln -s /usr/bin/python3.6 /usr/bin/python
echo "In container"
echo "Running $@"
$@
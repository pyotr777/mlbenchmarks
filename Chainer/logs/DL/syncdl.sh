#!/bin/bash
# Sync Down with DL server

rsync -avc $@ --size-only --include=*.log --include=*.csv --include=*/ --exclude=.* --exclude=* DL:/data1/peter/Chainer/logs/ .
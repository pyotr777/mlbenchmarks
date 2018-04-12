#!/bin/bash
# Sync UP with DL server

rsync -avc $@ --size-only --include=*.log --include=*.csv --include=*/ --exclude=.* --exclude=* DL:/data1/peter/image-caption-applications/logs/ .
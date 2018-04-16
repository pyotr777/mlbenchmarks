#!/bin/bash
# Sync UP with DL server

rsync -avc $@ --size-only --include=*.log --include=*.csv --include=*/ --exclude=.* --exclude=* mouse-pub:/home/peter/logs/ .
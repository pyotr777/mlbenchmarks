#!/bin/bash
# Sync UP with DL server

rsync -avc $@ --size-only --exclude=syncupdl.sh --include=*.py --include=*.sh --exclude=.* --exclude=* . DL:/data1/peter/image-caption-applications/
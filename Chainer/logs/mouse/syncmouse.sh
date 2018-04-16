#!/bin/bash
# Sync DOWN with Mouse server

rsync -avc $@ --size-only --include=*.log --include=*.csv --include=*/ --exclude=.* --exclude=* mouse:logs/ .
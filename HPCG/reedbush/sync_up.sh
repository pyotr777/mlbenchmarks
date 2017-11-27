#!/bin/bash

REMOTE_HOST="i96005@reedbush.cc.u-tokyo.ac.jp"
REMOTE_DIR="lustre/HPCG/hpcg3.1"
echo "rsync from local to remote $REMOTE_HOST:$REMOTE_DIR/"
set -x
rsync -avc $@  --exclude="sync*" --include-from="include.txt" --exclude="*" . $REMOTE_HOST:$REMOTE_DIR/
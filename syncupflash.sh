#!/bin/bash

# Synchronise with external flash drive

usage=$(cat <<USAGEBLOCK
Usage:
$0 [-d <path>] [-n]

Options:
    -d          External drive path
    -n          Dry run
    -h, --help  This help info.
USAGEBLOCK
)


# Default parameteres
FLASH_PATH="/Volumes/WENDE32GB/MLbenchmark_logs"
RSYNC_OPTIONS="-avcz"

while test $# -gt 0; do
    case "$1" in
        -h | --help)
            echo "$usage"
            exit 0
            ;;
        -d)
            FLASH_PATH="$2";shift;
            ;;
        -n)
            RSYNC_OPTIONS=$RSYNC_OPTIONS"n"
            ;;
        --debug)
            debug=YES
            ;;
        --)
            shift
            break;;
        -*)
            MORE_OPTIONS="$1"
            ;;
        *)
            echo "Unknown option $1";
            echo "$usage"
            exit 1
            ;;
    esac
    shift
done

if [[ ! -d "$FLASH_PATH" ]]; then
    echo "Path $FLASH_PATH not found"
    exit 1
fi

echo "$RSYNC_OPTIONS $MORE_OPTIONS"
set -x
rsync $RSYNC_OPTIONS $MORE_OPTIONS \
    --prune-empty-dirs \
    --exclude=".*" \
    --filter="+ nvvp/*" --filter="+ */nvvp/" \
    --filter="+ logs/*/*/*/*" --filter="+ logs/*/*/*" --filter="+ logs/*/*" --filter="+ logs/*" --filter="+ */logs/" \
    --include="CUDNN7/*" --include="CUDNN7" \
    --include="combine_profiles" --include="Chainer" --include="image-caption" \
    --include="*.csv" --include="*.nvvp" --include="*.log" \
    --exclude="*" . $FLASH_PATH
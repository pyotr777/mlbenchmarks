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
RSYNC_OPTIONS="-avc"

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
            RSYNC_OPTIONS="-anvc"
            ;;
        --debug)
            debug=YES
            ;;
        --)
            shift
            break;;
        *)
            echo "Unknown parameter $1";
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

echo $RSYNC_OPTIONS
set -x
rsync $RSYNC_OPTIONS --include="logs" --include="Chainer" --include="combine_profiles" --include="image-caption" --include="*.csv" --include="*.nvvp" --include="*.log" --exclude="*" . $FLASH_PATH
#!/usr/bin/env bash
set -eu -o pipefail

if [ "$#" -ne 2 ]; then
    echo "Flash an image to a device"
    echo "usage: $0 <SOURCE_IMG> <DEST_DEV>"
    exit 1
fi

if [ "${EUID}" -ne "0" ]; then
    echo "This script needs to be run as root, to allow mounting / unmounting." 
    exit 1
fi

# check if dependencies exist
type pv >/dev/null

SOURCE_IMG=$1
DEST_DEV=$2

if [ "$(uname)" == "Darwin" ]; then
    echo "# Unmounting using diskutil"
    diskutil unmountDisk "${DEST_DEV}"
else
    echo "# Unmounting using umount"
    umount "${DEST_DEV}"*

    if mount | grep "${DEST_DEV}"; then
        echo "Error: A partition is still mounted."
        exit 1
    fi
fi

echo
echo "# Flashing image"
pv "${SOURCE_IMG}" | dd of="${DEST_DEV}" bs=1048576 2>/dev/null

echo "# Done: $(basename "$0")"

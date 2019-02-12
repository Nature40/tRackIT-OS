#!/usr/bin/env bash

if [ "$#" -ne 2 ]; then
    echo "usage: $0 <source_img> <dest_dev>"
    exit 1
fi

if [ `uname` == "Darwin" ]; then
    echo "# Unmounting using diskutil"
    diskutil unmountDisk "$2"
else
    echo "# Unmounting using umount"
    umount "$2"
fi

IMG_SIZE=`du -m "$1" | cut -f1`

echo
echo "# Flashing $IMG_SIZE MB"
dd if="$1" | pv -s ${IMG_SIZE}m | dd of="$2" bs=1048576


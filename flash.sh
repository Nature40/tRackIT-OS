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

IMG_PROPERTIES=(`ls -l LiftCar.img`)

echo
echo "# Flashing ${IMG_PROPERTIES[4]} bytes"
dd if="$1" 2>/dev/null | pv -s ${IMG_PROPERTIES[4]} | dd of="$2" bs=1048576 2>/dev/null


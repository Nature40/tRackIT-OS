#!/usr/bin/env bash

if [ "$EUID" -ne 0 ]; then 
    echo "Error: This script needs to be run as root."
    exit 1
fi

if [ -z "$1" ]; then
    echo "usage: $0 <harddisk>"
    exit 1
fi

DISK="$1"
echo "# Creating partition table on ${DISK}..."
fdisk ${DISK} <<EOF
g
n
1


w
EOF

PART=${DISK}1
echo "# Creating file system on ${PART}..."
echo y | mkfs.ext4 ${PART}

echo "# Done!"
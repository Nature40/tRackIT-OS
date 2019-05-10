#!/usr/bin/env bash

DISK="/dev/sdb"
DEVICE=${DISK}1

echo "# Creating partition table"
fdisk $DISK <<EOF
g
n
1


w
EOF

echo "# Creating file system"
sudo mkfs.ext4 $DEVICE

echo "# Done"
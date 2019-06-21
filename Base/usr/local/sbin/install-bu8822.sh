#!/usr/bin/env bash

DRIVERS_URL="http://downloads.fars-robotics.net/wifi-drivers/8822bu-drivers/"
wget -O 8822bu-drivers.html $DRIVERS_URL

for KERNEL in `ls /lib/modules`; do
    KERNEL_GREP=`echo $KERNEL | sed "s/+/-[0-9]*.tar.gz/"`
    TARFILE=`grep $KERNEL_GREP 8822bu-drivers.html | tail -n1 | cut -d\" -f8`

    echo "Kernel $KERNEL: $TARFILE, downloading..."
    wget $DRIVERS_URL$TARFILE -O $TARFILE
    tar xf $TARFILE

    mv 8822bu.conf /etc/modprobe.d/.
    chown root:root 8822bu.ko
    chmod 644 8822bu.ko
    mv 8822bu.ko /lib/modules/$KERNEL/

    rm install.sh
    rm $TARFILE
done

rm 8822bu-drivers.html
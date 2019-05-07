#!/usr/bin/env bash

echo "Running RasperryPi hostname configuration script..." 1>&2

HOSTNAME="nature40-sensorbox"
ID=`cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2 | cut -c9-16`

if [ "$ID" == "" ]; then
    echo "Error reading Raspberry Pi serial number, defaulting to $HOSTNAME" 1>&2
else
    HOSTNAME=${HOSTNAME}-$ID
fi

echo "Setting hostname: $HOSTNAME." 1>&2
hostnamectl set-hostname $HOSTNAME

echo "Done." 1>&2

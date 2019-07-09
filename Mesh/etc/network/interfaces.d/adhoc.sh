#!/usr/bin/env bash

ID=`cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2`

IP=10.0.$((16#${ID:12:2})).$((16#${ID:14:2}))/16

echo "Generating adhoc config..." 1>&2
echo "Address: $IP" 1>&2

cat <<EOF
auto wlan0
iface wlan0 inet static
    address $IP
    netmask 255.255.0.0
    wireless-channel 1
    wireless-essid nature40-sensorboxes-adhoc
    wireless-mode ad-hoc
EOF

echo "Done." 1>&2

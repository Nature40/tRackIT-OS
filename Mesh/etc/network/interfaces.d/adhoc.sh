#!/usr/bin/env bash

ID=`cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2`

IP1=$((16#${ID:8:2}))
IP2=$((16#${ID:10:2}))
IP3=$((16#${ID:12:2}))
IP4=$((16#${ID:14:2}))

echo "Generating adhoc config..." 1>&2
echo "Address: $IP" 1>&2

cat <<EOF
auto wlan0
iface wlan0 inet manual
    wireless-channel 1
    wireless-essid nature40-sensorboxes-adhoc
    wireless-mode ad-hoc
    # pre-select cell-id (faster connections)
    wireless-ap 90:43:ef:e0:be:e2
    address 169.254.$IP3.$IP4
    netmask 255.255.0.0

auto bat0
iface bat0 inet static
    # decrease mtu to cope with batman overhead / raspi zero w limitations
    mtu 1468
    pre-up /usr/sbin/batctl if add wlan0
    address 10.254.$IP3.$IP4
    netmask 255.255.0.0
EOF

echo "Done." 1>&2

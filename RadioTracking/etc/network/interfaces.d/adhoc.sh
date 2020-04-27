#!/usr/bin/env bash

ID=`cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2`

IP1=$((16#${ID:8:2}))
IP2=$((16#${ID:10:2}))
IP3=$((16#${ID:12:2}))
IP4=$((16#${ID:14:2}))

echo "Generating adhoc config..." 1>&2
echo "Address: $IP" 1>&2

cat <<EOF
allow-hotplug wlan0
iface wlan0 inet static
    address 169.254.$IP3.$IP4/16
    post-up ifconfig \$IFACE:0 169.254.0.1/16
    post-up   iptables --table nat --append POSTROUTING --out-interface \$IFACE --jump MASQUERADE
    post-down iptables --table nat --delete POSTROUTING --out-interface \$IFACE --jump MASQUERADE

EOF

echo "Done." 1>&2

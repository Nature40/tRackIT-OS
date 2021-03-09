#!/usr/bin/env bash

IFACE="wlan0"
SSID="${HOSTNAME}"

echo "Running RaspberryPi hostapd configuration script..." 1>&2
echo "$IFACE: $SSID / $PASS" 1>&2

cat <<EOF
interface=$IFACE
ssid=$SSID
wpa_passphrase=BirdsAndBats

wpa=2
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
auth_algs=1

hw_mode=g
ieee80211n=1
channel=1
country_code=DE

ctrl_interface=/var/run/hostapd
ctrl_interface_group=0
EOF

echo "Done." 1>&2

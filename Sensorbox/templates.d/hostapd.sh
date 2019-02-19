#!/usr/bin/env bash

mkdir -p /etc/hostapd

ID=`cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2 | sed 's/^0*//'`
SSID=nature40.liftbox.$ID

cat >/etc/hostapd/hostapd.conf <<EOF
interface=wlan0
ssid=$SSID
wpa_passphrase=BirdsArentReal

wpa=2
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
auth_algs=1

hw_mode=g
ieee80211n=1
require_ht=1

channel=1
country_code=DE
EOF

echo "### Written hostapd.conf for $SSID, restarting hostapd"
systemctl restart hostapd


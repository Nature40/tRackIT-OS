#!/usr/bin/env bash

ID=`cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2`

PRIVKEY=`printf $ID$ID | base64`
PUBKEY=`echo $PRIVKEY | wg pubkey`

IP=172.16.$((16#${ID:12:2})).$((16#${ID:14:2}))/16

echo "Generating wireguard config..." 1>&2
echo Public Key: $PUBKEY 1>&2
echo Address:  $IP 1>&2

cat <<EOF
[Interface] # rpi: $ID
Address = $IP
PrivateKey = $PRIVKEY

`cat /boot/nature40-servers.conf`
EOF

echo "Done." 1>&2

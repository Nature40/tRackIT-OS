#!/usr/bin/env bash
set -e

PRIVKEY=`cat "/boot/$HOSTNAME.wgkey"`
PUBKEY=`echo $PRIVKEY | wg pubkey`

# compute IP from HOSTNAME remainder
IP3=$((16#${HOSTNAME: -4: -2}))
IP4=$((16#${HOSTNAME: -2}))
IP="172.16.${IP3}.${IP4}/16"

echo "Generating wireguard config..." 1>&2
echo Public Key: $PUBKEY 1>&2
echo Address:  $IP 1>&2

cat <<EOF
[Interface] # $HOSTNAME
Address = $IP
PrivateKey = $PRIVKEY

`cat /boot/nature40-servers.conf`
EOF

echo "Done." 1>&2

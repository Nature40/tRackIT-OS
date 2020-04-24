#!/usr/bin/env bash

ID=`cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2`

IP1=$((16#${ID:8:2}))
IP2=$((16#${ID:10:2}))
IP3=$((16#${ID:12:2}))
IP4=$((16#${ID:14:2}))

echo "Generating dhlcient config..." 1>&2
echo "Address: $IP" 1>&2

cat <<EOF
option rfc3442-classless-static-routes code 121 = array of unsigned integer 8;

send host-name = gethostname();
request subnet-mask, broadcast-address, time-offset, routers,
	domain-name, domain-name-servers, domain-search, host-name,
	dhcp6.name-servers, dhcp6.domain-search, dhcp6.fqdn, dhcp6.sntp-servers,
	netbios-name-servers, netbios-scope, interface-mtu,
	rfc3442-classless-static-routes, ntp-servers;

interface "bat0" {
    send dhcp-requested-address 10.254.$IP3.$IP4;
}

EOF

echo "Done." 1>&2

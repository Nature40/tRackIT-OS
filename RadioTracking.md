# RadioTracking Scratchpad

The RTL devices can be permanently configured using their EEPROM, especially the serial numbers can be configured this way.

```bash
pi@nature40-sensorbox-a9d5abd2:~ $ rtl_eeprom -s red
Found 1 device(s):
  0:  Generic RTL2832U OEM

Using device 0: Generic RTL2832U OEM
Found Rafael Micro R820T tuner

Current configuration:
__________________________________________
Vendor ID:		0x0bda
Product ID:		0x2838
Manufacturer:		Realtek
Product:		RTL2838UHIDIR
Serial number:		00000001
Serial number enabled:	yes
IR endpoint enabled:	yes
Remote wakeup enabled:	no
__________________________________________

New configuration:
__________________________________________
Vendor ID:		0x0bda
Product ID:		0x2838
Manufacturer:		Realtek
Product:		RTL2838UHIDIR
Serial number:		red
Serial number enabled:	yes
IR endpoint enabled:	yes
Remote wakeup enabled:	no
__________________________________________
Write new configuration to device [y/n]? y 
Configuration successfully written.
Please replug the device for changes to take effect.
```

## Color-matched serial numbers

Every stick gets one of the serial numbers *red*, *yellow*, *green* or *blue* and is adressed by this value. However, Sticks cannot be tracked across devices and if a *red* stick is broken, it needs to be replaced by a stick configured to be *red*. 

Pro:
- On-device tracking of broken sticks
- Stickers to mark color and thus enhance handling in the field

Cons:
- To replace a stick, a correctly programmed one needs to be available.

## Retrieve Serial Numbers

1. Boot the Raspberry Pi with an appropriate Image
2. Join the ad-hoc network with an IP address matching the network : `169.254.xxx.xxx`
3. Broadcast ping all devices: `ping -b 169.254.255.255`
4. Look at the addresses answering the pings
5. Login to the device `ssh pi@...`
6. Get the serial number: `cat /proc/cpuinfo | grep Serial`


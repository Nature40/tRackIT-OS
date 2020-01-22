# RadioTracking Scratchpad

The RTL devices can be permanently configured using their EEPROM, especially the serial numbers can be configured this way.

```bash
pi@nature40-sensorbox-a9d5abd2:~ $ yes | rtl_eeprom -s 40000002
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
Serial number:		40000001
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
Serial number:		40000002
Serial number enabled:	yes
IR endpoint enabled:	yes
Remote wakeup enabled:	no
__________________________________________
Write new configuration to device [y/n]? 
Configuration successfully written.
Please replug the device for changes to take effect.
```

## Generating Serial Numbers 

One can think of different ways to create such serial numbers. 

### 1. Per-device serial numbers

At bootup, all devices would be iterated and unnamed sticks would be named according to the hostname and their index. 

This would have the benefit, that no configuration is required beforehand, sticks can be addressed at the local system and the service activation can be generic.

Pro: 
- Easy implementation
- Zero configuration

## 2. Global Serial Numbers

Writing a permanent serial number has the advantage, that damaged sticks can be tracked across their lifetime and isolated more easily, as well as a fixed matching to the points of the compass. 

However, the OS needs to be configured to use the correct serial numbers, i.e. start the signal_detect service on the correct serial numbers. 

Pro: 
- Tracking across multiple all deployments

Con:
- Implementation and configuration overhead

## 3. Simple Serial Numbers

Every stick gets one of the serial numbers *south*, *west*, *north* or *east* and is adressed by this value. However, Sticks cannot be tracked across devices and if a *southern* stick is broken, it needs to be replaced by a stick configured to be a *south*. 

Pro:
- On-device tracking of broken sticks
- Stickers to mark compass direction and thus enhance handling in the field?

Cons:
- To replace a stick, a correctly programmed one needs to be available.
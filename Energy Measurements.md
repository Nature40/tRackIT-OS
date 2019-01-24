## Mass Storage
 - Sabrent USB3 SATA Converter + Kingston SSD
 - `umount /media/storage`: no effect
 - disconnect USB: -0.34 A

## Ethernet
 - `ifconfig eth0 down`: no effect
 - removing physical connection: -0.03 A 
 - `uhubctl/uhubctl -a0 -p1`: -0.04 A (in addition to physical disconnect) / -0.07
 
## TTGO LoRa Modem
 - removing physical connection: -0.11 A

## USB Audio Microphone
 - no effects at all (neither power down, nor no record, ...)

## AMBOLOVE AC1200 WiFi (ad-hoc mode)

- removing physical connection: -0.01A
- idle / off: -0.09A

## Raspberry Pi

### HDMI Output
 - `/usr/bin/tvservice -o`: -0.02 A

### Disable LEDs
 - `echo 0 > /sys/class/leds/led0/brightness`: -0.002 A
 - `echo 0 > /sys/class/leds/led1/brightness`: -0.002 A

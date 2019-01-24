# LiftCar (Moon)

LiftCar is a sensorbox of the type moon measuring at diferent levels of the forest. It works together with the LiftSystem (planet) and controls its position with its help.

## Peripherals

- Raspberry Pi Camera V2.1
- TSL2561 Light Sensor
- AM2302 Temerature & Humidity Sensor
- Microphone (tbd)
- DS3231 Real-Time-Clock (LED removed)
- Powerbank: EasyAcc 26000 (26 Ah * 3.3V = 85.8 Wh)

## Energy considerations

- minimal power consumption in idle mode: 0.18 A == ~1 W
- maximal runtime: 85,8 Wh / 5.14 V / 0.18 A = 92,7 h = ~3d 20h

## Setup Gesamtsystem

Bootup: 0.9 A
Measurement: 0.78 A
Idle: 0.65 A

### Disableing Services:

 - picam delta: 0.14 A
 - piaudio delta: <0.01 A
 - pitemp / pilux delta: <0.01 A / 0.1 A in measurement

#### Mass Storage
 - `umount /media/storage`: no effect
 - `uhubctl/uhubctl -a0 -p2`: (storage connected via port 2): -0.34 A

### Ethernet
 - removing physical connection: -0.03 A 
 - `ifconfig eth0 down`: no effect
 - `uhubctl/uhubctl -a0 -p1`: -0.04 A (in addition to physical disconnect) / -0.07
 
### TTGO LoRa Modem
 - Deep Sleep: -0.08 A
 - `uhubctl/uhubctl -a0 -p1`: -0.11 A

### USB Audio Microphone
 - no effects at all (neither power down, nor no record, ...)

### HDMI Output
 - `/usr/bin/tvservice -o`: -0.02 A

### Disable LEDs
 - `echo 0 > /sys/class/leds/led0/brightness`: -0.00 A
 - `echo 0 > /sys/class/leds/led1/brightness`: -0.00 A

## Setup Einzelkomponenten

- Blaues USB Power Meter
- an Powered USB Hub
- USB 2 Passthrough

### Sabrent SATA 3 Adapter + Kingston SSD

- During Mount: 0.30 A
- Idle: 0.10 A
- Unmounted: 0.10 A
- Write: 0.18 A
- Read: 0.15 A

### AMBOLOVE AC1200 WiFi

- Idle: 0.01A
- AdHoc-Mode: 0.09A

### TTGO LoRa 

- Idle: 0.09 A

### USB Microphone

- Idle: 0.01 A
- Recording: 0.01 A
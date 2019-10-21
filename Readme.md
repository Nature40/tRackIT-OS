# Natur 4.0: Sensorboxes

[![Build Status](https://travis-ci.org/Nature40/Sensorboxes-Images.svg?branch=master)](https://travis-ci.org/Nature40/Sensorboxes-Images)

This repo collects software and hardware descriptions and links used in Natur 4.0 Sensorboxes. It contains distribution definitions (using pimod) and configuration files for sensorboxes.

## Overview

An installation currently consist of those parts:

 - [LiftSystem](https://github.com/Nature40/Satellite-LiftSystem): stateless ESP32 Board and Motor Driver to run the Lift
 - LiftBox: various Sensors, running up and down
 - PlanetBox: various sensors, Harddrive as data sink, LTE uplink

## Configuration

To setup an installation one has to install the prepared images to the devices and configure them. The configuration mainly consists of adapting the static config (`/boot/sensorproxy.yml`) as well as the measurement cycle (`/boot/meterings.yml`).

More details can be found in [pysensorproxy Readme](https://github.com/nature40/pysensorproxy).

## Network Auto Configuration

The IP addresses are autoconfigured using a set of scripts ([Wi-Fi](https://github.com/Nature40/Sensorboxes-Images/blob/master/Mesh/etc/network/interfaces.d/adhoc.sh), [Wireguard](https://github.com/Nature40/Sensorboxes-Images/blob/097da475bb3748acea959cec190717a0ae4b5ee1/Base/etc/wireguard/nature40.conf.sh)) run at bootup. The prefixes are assigned statically, while the dynamic part is computed using the Rasperry Pi Serial number. 

  - Ad-hoc Wi-Fi Network: 169.254.X.X
  - B.A.T.M.A.N Mesh: 10.254.X.X
  - Wireguard: 172.16.X.X
 
An IP adress list used for Nature 4.0 [can be found here (private)](https://github.com/Nature40/Sensorboxes-Config/blob/master/hosts).

## Useful commands

##### pysensorproxy daemon control

```bash
# control daemon
sudo systemctl start sensorproxy
sudo systemctl stop sensorproxy
systemctl status sensorproxy

# view logs
journalctl -u sensorproxy

# follow current log
journalctl -fu sensorproxy

# run standalone instance
sudo sensorproxy -vv --config /boot/sensorproxy.yml --metering /boot/meterings.yml
```

## Build Distro

A distribution can be build by using pimod. This tutorial will use the provided `docker-compose` file.

```bash
# first update / init the submodules
git submodule update --init --recursive

# download the required raspbian image
wget http://downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2019-07-12/2019-07-10-raspbian-buster-lite.zip
unzip 2019-07-10-raspbian-buster-lite.zip

# build the Base, Mesh and Sensorbox image
docker-compose run pimod pimod.sh Base.Pifile
docker-compose run pimod pimod.sh Mesh.Pifile
docker-compose run pimod pimod.sh Sensorbox.Pifile
```

```bash
$ docker-compose run pimod pimod.sh Sensorbox.Pifile
### FROM 2018-11-13-raspbian-stretch-lite.img
### TO LiftCar.img
### PUMP 100
100+0 records in
100+0 records out
104857600 bytes (105 MB, 100 MiB) copied, 0.929542 s, 113 MB/s
e2fsck 1.43.4 (31-Jan-2017)
Pass 1: Checking inodes, blocks, and sizes
Pass 2: Checking directory structure
Pass 3: Checking directory connectivity
Pass 4: Checking reference counts
Pass 5: Checking group summary information
rootfs: 39646/110880 files (0.1% non-contiguous), 258346/443392 blocks
resize2fs 1.43.4 (31-Jan-2017)
The filesystem is already 443392 (4k) blocks long.  Nothing to do!

Disk /dev/loop0: 1.9 GiB, 1971322880 bytes, 3850240 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0x7ee80803

Device       Boot Start     End Sectors  Size Id Type
/dev/loop0p1       8192   98045   89854 43.9M  c W95 FAT32 (LBA)
/dev/loop0p2      98304 3645439 3547136  1.7G 83 Linux
loop deleted : /dev/loop0
### RUN raspi-config nonint do_serial 0
...
```

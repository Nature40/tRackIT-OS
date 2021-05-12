# tRackIT OS
[![Build Images](https://github.com/Nature40/tRackIT-OS/actions/workflows/build_images.yml/badge.svg)](https://github.com/Nature40/tRackIT-OS/actions/workflows/build_images.yml)

Open-source Software for Reliable VHF Wildlife Tracking

## Configuration

The system can be configured through different files in the `/boot` partition.

### `boot/cmdline.txt`

`cmdline.txt` holds the kernel boot commandline, which allows to configure the hostname in newer systemd versions. This behavioud is emulated and a hostname can be configured by setting `systemd.hostname=tRackIT-00001`

### [`/boot/radiotracking.ini`](boot/radiotracking.ini)

Hold the configuration of `pyradiotracking`, [see example config](https://github.com/Nature40/pyradiotracking/blob/master/etc/radiotracking.ini).

### [`/boot/mqttutil.conf`](boot/mqttutil.conf)

Mqttutil reports system statistics via MQTT, [see example config](https://github.com/Nature40/pymqttutil/blob/main/etc/mqttutil.conf).


### `/boot/wireguard.conf`

A wireguard configuration can be set using this configuration file. 

### [`/boot/mosquitto.d/`](boot/mosquitto.d/)

Files in this directory are loaded by mosquitto. E.g. mqtt brokers for reporting can be set using files in this folder.


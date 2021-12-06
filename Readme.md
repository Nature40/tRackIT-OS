# tRackIT OS
[![Build Images](https://github.com/Nature40/tRackIT-OS/actions/workflows/build_images.yml/badge.svg)](https://github.com/Nature40/tRackIT-OS/actions/workflows/build_images.yml)

tRackIT OS is an open-source software for reliable VHF radio tracking of (small) animals in their wildlife habitat. tRackIT OS is an operating system distribution for tRackIT stations that receive signals emitted by VHF tags mounted on animals and are built from low-cost commodity-off-the-shelf hardware. tRackIT OS provides software components for VHF signal processing, system monitoring, configuration management, and user access. In particular, it records, stores, analyzes, and transmits detected VHF signals and their descriptive features, e.g., to calculate bearings of signals emitted by VHF radio tags mounted on animals or to perform animal activity classification. 

## Download

The image of tRackIT OS can be downloaded in the [GitHub Releases](https://github.com/Nature40/tRackIT-OS/releases) section of this repository. 

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

## Scientific Usage & Citation

If you are using tRackIT OS in academia, we'd appreciate if you cited our [scientific research paper](https://jonashoechst.de/assets/papers/hoechst2021tRackIT.pdf).

> J. Höchst & J. Gottwald et al., "tRackIT OS: Open-source Software for Reliable VHF Wildlife Tracking," in 51. Jahrestagung der Gesellschaft für Informatik, Digitale Kulturen, INFORMATIK 2021, Berlin, Germany, 2021.

```bibtex
@inproceedings{hoechst2021tRackIT,
  title = {{tRackIT OS: Open-source Software for Reliable VHF Wildlife Tracking}},
  author = {Höchst, Jonas and Gottwald, Jannis and Lampe, Patrick and Zobel, Julian and Nauss, Thomas and Steinmetz, Ralf and Freisleben, Bernd},
  booktitle = {51. Jahrestagung der Gesellschaft f{\"{u}}r Informatik, Digitale Kulturen, {INFORMATIK} 2021, Berlin, Germany},
  series = {{LNI}},
  publisher = {{GI}},
  month = sep,
  year = {2021}
}
```

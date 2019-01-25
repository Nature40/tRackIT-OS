# Sensorboxes

This repo contains distribution definitions (using pimod) and configuration files for sensorboxes in the context of the LOEWE Nature 4.0 project.

## Build Distro

A distribution can be build conviniently by using docker-compose:

```
$ docker-compose run pimod pimod.sh LiftCar.Pifile
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

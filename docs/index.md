---
menu: Quickstart
---

# Quickstart
In this quick start guide, we assume that a tRackIT station is already available and that it is now to be equipped and operated with the tRackIT OS.

## 1. Download OS image
As usual in the field of single boards like the Raspberry Pi, the Operating System (OS) is delivered as an image, i.e. a file that can be transferred directly to an SD card.
*tRackIT OS* can be downloaded at the [releases section of the respective Github repository](https://github.com/Nature40/tRackIT-OS/releases). 
Download the file *tRackIT-x.y.z.zip* of the most recent release. 
Pre-releases can also be tried out, but these may be untested and may not work to their full extent.


## 2. Flash Image
A particularly user-friendly alternative for flashing Operating System Images is [BalenaEtcher](https://www.balena.io/etcher/), which is described here as an example. 
BalenaEtcher allows to unzip and flash the downloaded .zip file to an SD card:

* First, an SD card must be inserted into the computer.
* Second, the downloaded file is selected in BalenaEtcher using "Flash from File".
* Thirdly, the SD card is selected and the file is transferred by clicking on "Flash!".

![Animated GIF of a flashing process using BalenaEtcher.](assets/balenaetcher.gif)

> Note: BalenaEtcher might ask for permissions to be granted.


## 3. Configure Station
After flashing the card, remove and insert the SD card again to access the `boot` partition.
There are multiple files containing the configuration of the station:

* Hostname: The last entry of `cmdline.txt` contains the hostname which can be set according to [Linux hostname rules](https://man7.org/linux/man-pages/man7/hostname.7.html). Valid characters for hostnames are ascii letters from a to z, the digits from 0 to 9, and the hyphen (-).
* Wireguard VPN: *tRackIT OS* supports remote access through wireguard. A configuration file named `wireguard.conf` can be added to the boot partition to enable the feature.
* Signal Detection: The signal detection algorithm's configuration can be adjusted in the `radiotracking.ini` file.
* MQTT Server: A custom MQTT server can be configured the the configuration files in the `mosquitto.d` directory.


## 4. Deploy Station
Safely remove the SD card from your computer and insert it into the *tRackIT station's* Raspberry Pi and boot the station by connecting the power cable.

> Note: The first boot takes up to a few minutes, depending on the speed and size of the SD card, because the file system is still adjusted to the size. 

The station can be accessed through Wi-Fi, where the network name (SSID) is the previously configured hostname. 
The default password is `BirdsAndBats`.

The *tRackIT station* uses the IPv4 address 169.254.0.1 and a WebUI can be accessed via [http://169.254.0.1](http://169.254.0.1). 
There are multiple entries serving different purposes:

* `boot`: contents of the `boot` partition, i.e. the configuration,
* `radiotracking`: signal detection web interface and configuration screen,
* `sysdweb`: service control, i.e. start and stop services, access logfiles,
* `<hostname>`: data collected at the specific station.

### Check Sysdweb
To check that everything's working, first access `sysdweb` ([http://169.254.0.1/sysdweb](http://169.254.0.1/sysdweb)).
Sysdweb requires authentication, `tRackIT OS` uses the `pi` user's default passwort is `natur`. 

![Screenshot of the sysdweb user interface.](assets/sysdweb.png)

All services in green are up and running. 

> Note: *Huawei Check* is marked red, which in this case indicates, that it is currently not running. In this case this is fine, since it runs periodically rather than continuously. 

The log messages of the running services can be accessed by clicking the service name, which allows for further troubleshooting.

![Screenshot of the sysdweb user interface showing the log journal.](assets/sysdweb-journal.png)

> Note: In this particular case there are some warnings, that multiple signals detected on SDR 1 should be added to a matching signal. If this happens, the signal of lower dBW is discarded. 
> As this does only happen sporadically (17:05, 17:16 and 17:22) it does not mark a problem.

### Check RadioTracking
Next, access `radiotracking` to check if a nearby VHF transmitter is received correctly ([http://169.254.0.1/radiotracking](http://169.254.0.1/radiotracking)).

![Screenshot of the radiotracking user interface showing detected signals.](assets/radiotracking-signals.png)

The dots in blue indicate that a VHF transmitter is received on SDR 0 (north) which indicates signal detection is running correctly. 

## 5. Configuration & Calibration
*tRackIT stations* require to be calibrated when set up for the first time, since the used SDR devices differ in signal attenuation. To calibrate a station follow this routine: 

1. Place a VHF transmitter roughly 150 meters away from the station.
2. Access the *Configuration* pane, enable calibration mode and click *Save* and *Restart*.
3. Slowly and carefully rotate the stations antennas by at least 360° and back to the default orientation.
4. Find the frequency of your VHF transmitter in the *Graphs* pane and note or copy the calibration values.
5. Open the *Configuration* pane, disable the calibration mode and enter the calibration values into the respective fields and click *Save* and *Restart*.

![Calibration values presented in the *Graphs* pane.](assets/radiotracking-calibration.png)

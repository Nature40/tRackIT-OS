# Pysensorproxy

... is a python tool to schedule, execute and transmit environmental measurements. It is modulized by supporting various sensors configurable in a yaml file. The meterings are done according to a configurable schedule.

## Static configuration: *sensorproxy.yml*

All configuration to describe the configured hardware is to be found in the `sensorproxy.yml` file.

An example static configuration file can be found in [examples/sensorproxy.yml](examples/sensorproxy.yml), or here:

```yaml
sensors:                          # list of sensors
  am2302:                           # name (choose freely)
    type: AM2302                      # type (must be in sensorproxy.sensors.*)
    pin: 4                            # additional configuration parameter
  lumen:
    type: TSL2561
  cam:
    type: PiCamera
    img_format: jpeg

storage_path: /data               # path to save files

log:
  level: info                     # choose: critical, error, warning, info, debug, notset
  file_name: sensorproxy.txt

wifi:                             # wifi properties to be configured
  interface: wlan0                # the interface to be managed
  host_ap: true                   # open an access point if there is no outbounding connection

lift:                             # lift configuration
  ssid: nature40.liftsystem.709e
  height: 30
```

## Metering configuration: *meterings.yml*

The meterings are configured through a second file, an example file can be found in [examples/meterings.yml](examples/meterings.yml) and here:

In the following example both measuring cyles are independent from each other and as long as no shared ressources are used may run parallel. Conflicting access is prevented by using locks, whenever a sensor is accessed.

```yaml
daytime:              # name of the measuring cycle
  sensors:              # dict of the sensors to be measured
    cam:                  # reference to `cam`, configured in the static config (yml)
      res_X: 3280           # image resolution, set according to https://www.raspberrypi.org/documentation/raspbian/applications/camera.md
      res_Y: 2464
      adjust_time: 2s       # time to adjust to brightness
    mic:
      duration: 30s         # duration of the audio file to be recorded in seconds
  schedule:               # schedule parametes
    interval: 30m           # measurement is mandatory (max. 24h)
    start: 06h              # optional, according to local time
    end: 22h                # optional, according to local time
  heights: [0, 5]         # heights in meter

ongoing:					# 2nd measureing cycle
  sensors:
    am2302: {}              # empty config (no parameters possible here)
    lumen: {}
  schedule:
    interval: 5m
```

## Metering Process

The main thread of the programm only cares about scheduling, the measurements are realised threaded. To cope with conflicting access to resources each ressource is protected by a lock.

The meterings in the above example would both be scheduled independently and run the following steps:

- Acquire requested sensors
- If **height** is requested and 
  - acquire and connect **lift**
- For every **height**:
  - **move** to requested height
  - **measure** sensors threaded
- If **height** is requested
  - disconnect and release **lift**
- Release requested **sensors**


## Exception Handling

A target of this tool is resiliency of the measurements, so even if multiple sensors might not be available, the others should still be able to record. To reach this goal, every error should be logged but then coped with, even though the measurements might differ from defined behaviour. Examples:

- If the lift connection fails, meterings are done in the current height.
- tbd.

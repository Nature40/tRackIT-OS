import logging
import subprocess
import os

from .base import register_sensor, Sensor, Sensor, SensorNotAvailableException
from sensorproxy.wifi import WiFi, WiFiManager

logger = logging.getLogger(__name__)


@register_sensor
class RsyncSender(Sensor):
    def __init__(self, *args, ssid: str, psk: str, destination: str, **kwargs):
        super().__init__(*args, uses_height=False, **kwargs)

        self.destination = destination
        self.wifi = WiFi(ssid, psk)

    _header_sensor = [
        "Status",
    ]

    def _rsync_cmd(self):
        cmd = ["rsync", "-avz", "--remove-source-files", "--no-relative",
               "-e", "ssh -o StrictHostKeyChecking=no"]

        local_storage_path = os.path.join(
            self.proxy.storage_path, self.proxy.hostname)
        cmd.append(os.path.join(local_storage_path, "."))
        cmd.append(os.path.join(self.destination, self.proxy.hostname))

        return cmd

    def _read(self, **kwargs):
        if self.proxy.wifi_mgr:
            logger.info("connecting to WiFi '{}'".format(self.wifi.ssid))
            self.proxy.wifi_mgr.connect(self.wifi)
        else:
            logger.info("WiFi is handled externally.")

        logger.info("acquiring access to all sensors")
        for sensor in self.proxy.sensors.values():
            if sensor == self:
                continue

            sensor._lock.acquire()

        cmd = self._rsync_cmd()
        logger.info("Launching rsync: {}".format(" ".join(cmd)))

        p = subprocess.Popen(cmd)
        p.wait()

        if self.proxy.wifi_mgr:
            logger.info("disconnecting from WiFi")
            self.proxy.wifi_mgr.disconnect()

        # Call refresh on each Sensor.
        # This will create new filenames for each FileSensor atm.
        logger.debug("release locks to all sensors")
        for sensor in self.proxy.sensors.values():
            if sensor == self:
                continue

            sensor._lock.release()

        if p.returncode != 0:
            raise SensorNotAvailableException(
                "rsync returned {}".format(p.returncode))

        return [p.returncode]

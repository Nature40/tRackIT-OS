import os
import time
import uuid
import csv
import logging
import threading

from abc import ABC, abstractmethod
from typing import Type
from pytimeparse import parse as parse_time


logger = logging.getLogger(__name__)


class Sensor:
    """Abstract sensor class"""

    def __init__(self, proxy, name: str, uses_height: bool, ** kwargs):
        """
        Args:
            name (str): given name of the sensor
            storage_path (str): path to store files in
        """

        self.proxy = proxy
        self.name = name
        self.uses_height = uses_height

        self._filename_format = "{_class}/{_ts}-{_id}-{_sensor}-{_custom}"
        self.refresh()

        self._lock = threading.Lock()
        super().__init__()

    def _generate_filename(self, _ts: str, custom: [str] = []):
        return self._filename_format.format(
            _class=self.__class__.__name__,
            _ts=_ts,
            _id=self.proxy.id,
            _sensor=self.name,
            _custom="-".join(custom),
        )

    @staticmethod
    def _parse_filename(filename):
        basename, _file_ext = filename.split(".")
        metadata = basename.split("-")

        tags = dict(zip(["_id", "_class", "_sensor"], metadata[:3]))
        # TODO: Parse tags in custom headers, e.g. height for images

        return tags

    def refresh(self):
        """Refresh the sensor, e.g. creating a new file."""

        # set a valid file path
        file_name = self._generate_filename(Sensor.time_repr()) + ".csv"
        self.__file_path = os.path.join(
            self.proxy.storage_path, self.proxy.hostname, file_name)

        # create the regarding directory
        try:
            os.makedirs(os.path.dirname(self.__file_path))
        except FileExistsError:
            pass

        # initialize the file
        with open(self.__file_path, "a") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(self.header)
            csv_file.flush()

    def get_file_path(self):
        if not os.path.exists(self.__file_path):
            self.refresh()

        return self.__file_path

    @property
    def _header_start(self):
        if self.uses_height and self.proxy.lift:
            return ["Time (date)", "#Height (m)"]
        return ["Time (date)"]

    _header_sensor = []

    @property
    def header(self):
        return self._header_start + self._header_sensor

    @staticmethod
    def time_repr():
        """Current time, formatted."""

        return time.strftime("%Y-%m-%dT%H%M%S", time.gmtime())

    @abstractmethod
    def _read(self, **kwargs):
        """Read the sensor.

        Returns:
            [object]: Values of the sensor.
        """

        pass

    def record(self, count: int = 1, delay: str = "0s", tries=2, **kwargs):
        logger.debug("acquire access to {}".format(self.name))
        self._lock.acquire()
        records = []
        successful = 0

        try:
            for num in range(count * tries):
                try:
                    ts = Sensor.time_repr()
                    reading = self._read(**kwargs)
                    if len(reading) != len(self._header_sensor):
                        raise SensorNotAvailableException("Reading length ({}) does not match header length ({}).".format(
                            len(reading), len(self._header_sensor)))
                    self._publish(ts, reading, **kwargs)

                    records.append(reading)
                    successful += 1
                    logger.debug(
                        "Sensor '{}' measured correctly (try {}/{}, {} successful).".format(
                            self.name, num+1, count*tries, successful))

                    if successful < count:
                        time.sleep(parse_time(delay))
                    else:
                        break

                except SensorNotAvailableException as e:
                    logger.warn(
                        "Sensor '{}' measurement failed (try {}/{}, {} successful): {}".format(self.name, num+1, count*tries, successful, e))

        finally:
            if successful < count:
                logger.error(
                    "Sensor '{}': {} successful of {} requested measurements.".format(self.name, successful, count))

            logger.debug("release access to {}".format(self.name))
            self._lock.release()

        return records

    def _publish(self, ts, reading, influx_publish: bool = False, height_m: float = None, **kwargs):
        file_path = self.get_file_path()

        if self.uses_height and self.proxy.lift:
            row = [ts, height_m] + reading
        else:
            row = [ts] + reading

        with open(file_path, "a") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(row)
            csv_file.flush()

        if self.proxy.influx and influx_publish:
            logger.info("Publishing {} metering to Influx".format(self.name))

            def _publish_thread(self, row):
                try:
                    self.proxy.influx.publish(
                        header=self.header,
                        row=row,
                        _class=self.__class__.__name__,
                        _hostname=self.proxy.hostname,
                        _id=self.proxy.id,
                        _sensor=self.name,
                    )
                except Exception as e:
                    logger.warn("Publishing on infux failed: {}".format(
                        e), {"influx_publish": False})

            thread = threading.Thread(
                target=_publish_thread, args=(self, row))
            thread.start()

        return file_path


class FileSensor(Sensor):
    """Class for sensors logging more complex data to binary files."""

    def __init__(self, *args, file_ext: str, **kwargs):
        self.file_ext = file_ext
        super().__init__(*args, **kwargs)

    def generate_path(self):
        file_name = self._generate_filename(
            Sensor.time_repr()) + "." + self.file_ext
        return os.path.join(self.proxy.storage_path, self.proxy.hostname, file_name)


classes = {}


def register_sensor(cls: Type[Sensor]):
    """Add the sensor to the classes dict by its name."""
    classes[cls.__name__] = cls
    return cls


class SensorNotAvailableException(Exception):
    """Exception: cannot read sensor."""

    pass


class SensorConfigurationException(Exception):
    """Exception: configuration of the sensor doesn't work."""

    pass

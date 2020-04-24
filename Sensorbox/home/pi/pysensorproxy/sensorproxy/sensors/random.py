import time
import os
import random
import logging

from .base import register_sensor, Sensor, FileSensor

logger = logging.getLogger(__name__)


@register_sensor
class Random(Sensor):
    def __init__(self, *args, maximum=100, **kwargs):
        super().__init__(*args, uses_height=False, **kwargs)

        self.maximum = maximum

    _header_sensor = [
        "Random Integer",
    ]

    def _read(self, **kwargs):
        return [random.randint(0, self.maximum)]


@register_sensor
class RandomFile(FileSensor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, uses_height=False, file_ext="bin", **kwargs)

    _header_sensor = [
        "Filename",
    ]

    def _read(self, bytes, **kwargs):
        file_path = self.generate_path()

        with open(file_path, "ab") as file:
            file.write(os.urandom(bytes))

        return [file_path]

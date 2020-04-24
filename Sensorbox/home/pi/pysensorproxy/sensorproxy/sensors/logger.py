import time
import logging

from .base import register_sensor, Sensor, SensorNotAvailableException

logger = logging.getLogger(__name__)


@register_sensor
class LoggingHandler(logging.Handler, Sensor):
    def __init__(self, *args, level: str = "WARNING", logger_name: str = "sensorproxy", influx_publish=False, **kwargs):
        if level.upper() not in logging._nameToLevel:
            raise SensorNotAvailableException(
                "Level must be in {}.".format(logging._nameToLevel.keys()))

        level_num = logging._nameToLevel[level.upper()]
        logging.Handler.__init__(self, level_num)
        Sensor.__init__(self, *args, uses_height=False, **kwargs)

        root = logging.getLogger(logger_name)
        root.addHandler(self)

        self.influx_publish = influx_publish

    _header_sensor = [
        "#Name",
        "#Level",
        "Message",
    ]

    def record(self, **kwargs):
        raise SensorNotAvailableException(
            "The Logger sensor can't be called explicitly, but is called when writing to the log.")

    def emit(self, record):
        # influx publishing can be overwritten by supplying the extra argument in a dict
        # logger.warning("test", {"influx_publish": False})

        ts = self.time_repr()
        reading = [record.name, record.levelname, record.msg]

        if (record.args != None) and isinstance(record.args, dict) and "influx_publish" in record.args:
            self._publish(ts, reading, **record.args)
        else:
            self._publish(ts, reading, influx_publish=self.influx_publish)

import time
import logging

import Adafruit_DHT
import tsl2561
import w1thermsensor

from .base import register_sensor, Sensor, SensorNotAvailableException

logger = logging.getLogger(__name__)


@register_sensor
class AM2302(Sensor):
    def __init__(self, *args, pin: int, **kwargs):
        super().__init__(*args, uses_height=True, **kwargs)

        self.pin = pin

    _header_sensor = [
        "Temperature (°C)",
        "Humidity (%)",
    ]

    def _read(self, **kwargs):
        logger.debug("Reading AM2302 sensor on pin {}".format(self.pin))

        try:
            humid, temp = Adafruit_DHT.read(Adafruit_DHT.AM2302, self.pin)
        except RuntimeError as e:
            raise SensorNotAvailableException(e)

        if humid == None or temp == None:
            raise SensorNotAvailableException(
                "No AM2302 instance on pin {}".format(self.pin))

        humid = round(humid, 3)
        temp = round(temp, 3)
        logger.info("Read {}°C, {}% humidity".format(temp, humid))

        return [temp, humid]


@register_sensor
class DS18B20(Sensor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, uses_height=True, **kwargs)

    _header_sensor = [
        "Temperature (°C)",
    ]

    def _read(self, **kwargs):
        logger.debug("Reading DS18B20 sensor")

        try:
            sensor = w1thermsensor.W1ThermSensor()
            temp = sensor.get_temperature()
        except RuntimeError as e:
            raise SensorNotAvailableException(e)

        temp = round(temp, 3)
        logger.info("Read {}°C".format(temp))

        return [temp]


@register_sensor
class TSL2561(Sensor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, uses_height=True, **kwargs)

    _header_sensor = [
        "Illuminance (lux)",
        "broadband",
        "ir",
    ]

    def _read(self, **kwargs):
        logger.debug("Reading TSL2561 sensor via i2c")

        try:
            lux_sensor = tsl2561.TSL2561()
            broadband, ir = lux_sensor._get_luminosity()
            lux = lux_sensor._calculate_lux(broadband, ir)
        except OSError as e:
            raise SensorNotAvailableException(e)

        logger.info("Read {} lux (br: {}, ir: {})".format(lux, broadband, ir))

        return [lux, broadband, ir]

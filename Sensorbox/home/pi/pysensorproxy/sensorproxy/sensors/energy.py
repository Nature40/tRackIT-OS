import logging
import RPi.GPIO as gpio

from .base import register_sensor, Sensor

logger = logging.getLogger(__name__)


@register_sensor
class ChargingIndicator(Sensor):
    def __init__(self, *args, charging_incicator_pin: int = 13, **kwargs):
        super().__init__(*args, uses_height=False, **kwargs)
        gpio.setmode(gpio.BCM)

        self.charging_incicator_pin = charging_incicator_pin
        gpio.setup(charging_incicator_pin, gpio.IN)

    _header_sensor = [
        "Is Charging"
    ]

    def _read(self, **kwargs):
        charging = gpio.input(self.charging_incicator_pin)
        logger.info("Read Charging Indicator pin {}: {}".format(
            self.charging_incicator_pin, charging))

        return [charging]

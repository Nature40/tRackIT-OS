import time
import logging
import urllib
import json

from .base import register_sensor, Sensor, SensorNotAvailableException

logger = logging.getLogger(__name__)


@register_sensor
class TelekomVolume(Sensor):
    def __init__(self, *args, endpoint_uri: str = "http://pass.telekom.de/api/service/generic/v1/status", **kwargs):
        super().__init__(*args, uses_height=False, ** kwargs)

        self.endpoint_uri = endpoint_uri

    _header_sensor = [
        "Used Volume (MiB)",
        "Remaining Volume (MiB)",
        "Remaining Time (Days)",
    ]

    def _read(self, **kwargs):
        logger.debug("Reading Telekom data plan information.")

        try:
            status_request = urllib.request.Request(self.endpoint_uri)
            status_request.add_header('User-Agent', 'Mozilla/5.0')
            status_json = urllib.request.urlopen(status_request)
            status = json.loads(status_json.read().decode())

        except urllib.request.URLError as e:
            raise SensorNotAvailableException(
                "status json could not be loaded: {}".format(e))

        except json.decoder.JSONDecodeError as e:
            raise SensorNotAvailableException(
                "response json could not be parsed (are you connected via cellular?): {}".format(e))

        usedVolume = float(status["usedVolume"]) / 1024 / 1024
        initialVolume = float(status["initialVolume"]) / 1024 / 1024
        remainingVolume = initialVolume - usedVolume
        remainingTime = float(status["remainingSeconds"]) / 60 / 60 / 24

        logger.info("{} / {} MiB remaining for {} days.".format(usedVolume,
                                                                initialVolume, remainingTime))

        return [usedVolume, remainingVolume, remainingTime]

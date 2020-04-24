import os
import logging

from .base import register_sensor, Sensor, SensorNotAvailableException


logger = logging.getLogger(__name__)


@register_sensor
class Sink(Sensor):
    """ Sink consumes all files from a given directory and publishes their content 
    via different methods, including InfluxDB (more yet to come). After beeing consumed
    the files are moved away from the incoming directory.
    """

    def __init__(self, *args, input_directory, **kwargs):
        super().__init__(*args, file_ext=None, uses_height=False, **kwargs)

        # create input directory
        try:
            os.makedirs(input_directory)
        except FileExistsError:
            pass

        # allow everybody to write to input directory
        os.chmod(input_directory, 0o777)

        self.input_directory = input_directory

    def _consume_influx(self, file_path: str, _hostname: str, _id: str, _class: str, _sensor: str):
        if not file_path.endswith(".csv"):
            logger.debug("ignoring non-csv file")
            return

        logger.info("Sending {} to InfluxDB".format(file_path))

        try:
            file_name = os.path.basename(file_path)
            tags = self._parse_filename(file_name)

            self.proxy.influx.publish_csv(
                csv_path=file_path,
                _hostname=_hostname,
                **tags,
            )
        except Exception as e:
            logger.warn("Publishing on infux failed: {}".format(e))

    def record(self, influx_publish: bool = True, ** kwargs):
        if not os.path.isdir(self.input_directory):
            raise SensorNotAvailableException(
                "Input directory '{}' is not existing.".format(self.input_directory))

        for _hostname in os.listdir(self.input_directory):
            host_dir_input = os.path.join(self.input_directory, _hostname)

            # ignore files in the input directory itself
            if not os.path.isdir(host_dir_input):
                continue

            logger.info("consuming data from {}".format(_hostname))

            # create host directory for moving
            host_dir = os.path.join(self.proxy.storage_path, _hostname)
            try:
                os.makedirs(host_dir)
            except FileExistsError:
                pass

            for file_name in os.listdir(host_dir_input):
                # skip files with leading . (probably currently rsynced)
                if file_name.startswith("."):
                    continue

                file_path_incoming = os.path.join(host_dir_input, file_name)

                # parse filename according to convention
                _id, _class, _sensor = file_name.split("-")[:3]

                # call the different consumers
                if influx_publish:
                    self._consume_influx(
                        file_path_incoming, _hostname, _id, _class, _sensor)

                # move the file away to avoid double-consumption
                file_path = os.path.join(host_dir, file_name)
                os.rename(file_path_incoming, file_path)

            # remove empty folder
            try:
                os.rmdir(host_dir_input)
            except OSError as e:
                logger.info(
                    "couldn't remove folder of {}: {}".format(_hostname, e))

    def refresh(self):
        pass

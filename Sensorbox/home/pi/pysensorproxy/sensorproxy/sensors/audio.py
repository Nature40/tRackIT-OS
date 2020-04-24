import subprocess
import logging
import os

from pytimeparse import parse as parse_time

from .base import register_sensor, FileSensor, SensorNotAvailableException, SensorConfigurationException

logger = logging.getLogger(__name__)

AUDIO_FORMATS = ["wav", "flac"]


@register_sensor
class Microphone(FileSensor):
    def __init__(self, *args, audio_format: str, card: int, device: int, sample_format: str, rate: int, level: str, **kwargs):
        if audio_format not in AUDIO_FORMATS:
            logger.error(
                "Microphone sample format '{}' is not available, defaulting to 'wav'.".format(
                    self.file_ext
                )
            )
            audio_format = "wav"

        super().__init__(*args, file_ext=audio_format, uses_height=True, **kwargs)

        self.card = card
        self.device = device
        self.sample_format = sample_format
        self.rate = rate
        self.audio_format = audio_format

        try:
            self._set_volume(level)
        except SensorConfigurationException as e:
            logger.error(
                "Microphone configuration error (continuing): {}".format(e))

    def _set_volume(self, level: str):
        cmd = ["amixer", "-c", str(self.card), "sset", "Mic", str(level)]

        logger.debug("Setting microphone level: {}".format(" ".join(cmd)))

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        p.wait()
        stderr = p.stderr.read()

        if p.returncode != 0:
            raise SensorConfigurationException(
                "amixer returned {}: {}".format(p.returncode, stderr.decode())
            )

    def _read(self, file_path: str, duration: str, **kwargs):
        device_name = "hw:{},{}".format(self.card, self.device)
        duration_s = parse_time(duration)

        if self.file_ext == "wav":
            save_cmd = "{file_path}".format(file_path=file_path)
        elif self.file_ext == "flac":
            save_cmd = "| flac - -s -o {file_path}".format(file_path=file_path)

        cmd = "arecord -q -D {device_name} -t wav -f {sample_format} -r {rate} -d {duration_s} {save_cmd}".format(
            device_name=device_name,
            sample_format=self.sample_format,
            rate=self.rate,
            duration_s=duration_s,
            save_cmd=save_cmd,
        )

        logger.debug("Recording audio: '{}'".format(cmd))

        p = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        p.wait()
        err_msg = p.communicate()[0]

        if p.returncode != 0:
            raise SensorNotAvailableException(
                "arecord returned {}: '{}'".format(p.returncode, err_msg)
            )

        logger.info("audio file written to '{}'".format(file_path))

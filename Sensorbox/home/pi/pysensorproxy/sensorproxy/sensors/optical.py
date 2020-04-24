import time
import logging
import os
import glob

import picamera
from pytimeparse import parse as parse_time

from .base import register_sensor, FileSensor, SensorNotAvailableException

logger = logging.getLogger(__name__)


@register_sensor
class PiCamera(FileSensor):
    def __init__(self, *args, img_format: str, **kwargs):
        super().__init__(*args, uses_height=True, file_ext=img_format, ** kwargs)

        self.format = img_format

    def _read(self, file_path: str, res_X: int, res_Y: int, adjust_time: str, **kwargs):
        adjust_time_s = parse_time(adjust_time)

        logger.debug("Reading PiCamera with {}x{} for {}s".format(
            res_X, res_Y, adjust_time_s))

        try:
            with picamera.PiCamera() as camera:
                camera.resolution = (res_X, res_Y)
                camera.start_preview()
                time.sleep(adjust_time_s)

                camera.capture(file_path, format=self.format)
                camera.stop_preview()
        except picamera.exc.PiCameraMMALError as e:
            raise SensorNotAvailableException(e)
        except picamera.exc.PiCameraError as e:
            raise SensorNotAvailableException(e)

        logger.info("image file written to '{}'".format(file_path))


@register_sensor
class PiNoirCamera(PiCamera):
    pass


@register_sensor
class IRCutCamera(PiCamera):
    """Special extension for IR Cut cameras with switchable IR Filter

    The IR filter on the IR Cut Cameras are controlled by pin used for the 
    camera led in the first versions of the pi camera. 

    Usually the led can be deactivated by setting matching boot options, 
    e.g., `disable_camera_led=1`. This option is discontinued in newer 
    versions of raspbian.

    Another method of deactivating the IR filter is, to manually set the led
    gpio, usually supported by raspistill and the python picamera library. 
    Since the Raspberry Pi 3 B has Bluetooth, there where no GPIOs left, thus
    the led was re-routed to GPIO expander: https://picamera.readthedocs.io/en/release-1.13/api_camera.html?highlight=led#picamera.PiCamera.led

    The method implemented here, is to manually set the led pin using sysfs.
    For this method, one has to find out the gpio the led is connected to, which
    is achievable looking at the rpi firmware blob: https://github.com/raspberrypi/firmware/blob/master/extra/dt-blob.dts
    When searching for `CAMERA_0_LED`, the different GPIOs become visible,
    the offset for external GPIOs is 128, so an external GPIO 6 becomes 
    GPIO 134.
    """

    def __init__(self, *args, cam_led: int = 6, gpiochip_labels: [str] = ["raspberrypi-exp-gpio", "brcmexp-gpio"], **kwargs):
        super().__init__(*args, **kwargs)

        gpio_base = self.__gpiochip_label_base(gpiochip_labels)
        self.cam_gpio = gpio_base + cam_led
        self.cam_gpio_path = "/sys/class/gpio/gpio{}/value".format(
            self.cam_gpio)

        # export the requested gpio port
        if not os.path.exists(self.cam_gpio_path):
            with open("/sys/class/gpio/export", "a") as gpio_export_file:
                gpio_export_file.write(str(self.cam_gpio))

    @staticmethod
    def __gpiochip_label_base(gpiochip_labels):
        for gpiochip_path in glob.glob("/sys/class/gpio/gpiochip*/"):
            with open(os.path.join(gpiochip_path, "label"), "r") as gpiochip_label_file:
                label = gpiochip_label_file.readline().strip()

            if label in gpiochip_labels:
                with open(os.path.join(gpiochip_path, "base"), "r") as gpiochip_base_file:
                    base = int(gpiochip_base_file.readline())

                return base

        raise SensorNotAvailableException(
            "Could not find gpio base for {}".format(gpiochip_labels))

    def _read(self, file_path: str, res_X: int, res_Y: int, adjust_time: str, filter_ir: bool = False, **kwargs):
        adjust_time_s = parse_time(adjust_time)

        logger.debug("Reading IrCutCamera with {}x{} for {}s".format(
            res_X, res_Y, adjust_time_s))

        try:
            with picamera.PiCamera() as camera:
                camera.resolution = (res_X, res_Y)
                camera.start_preview()

                # set cam gpio to the matching value
                with open(self.cam_gpio_path, "a") as gpio_file:
                    gpio_file.write(str(int(filter_ir)))
                    time.sleep(2)

                time.sleep(adjust_time_s)

                camera.capture(file_path, format=self.format)
                camera.stop_preview()
        except picamera.exc.PiCameraMMALError as e:
            raise SensorNotAvailableException(e)
        except picamera.exc.PiCameraError as e:
            raise SensorNotAvailableException(e)

        logger.info("image file written to '{}'".format(file_path))

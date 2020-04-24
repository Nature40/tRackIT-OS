import subprocess
import tempfile
import base64
import logging
import signal
import threading

logger = logging.getLogger(__name__)


class WiFi:
    """Class to hold configuration of a WiFi Network."""

    def __init__(self, ssid, psk):
        """
        Args:
            ssid (str): WiFi SSID
            psk (str): WiFi pre-shared key
        """

        self.ssid = ssid
        self.psk = psk

    def _generate_config(self):
        """Generates a wpa_supplicant config file from the configuration.

        Returns:
            str: path to the generated config file
        """

        base64_name = base64.encodestring(
            self.ssid.encode()).decode()[:-1]
        config_path = "/tmp/wpa_{}.conf".format(base64_name)

        logger.debug("generating wpa config at {}".format(config_path))

        p = subprocess.Popen(["wpa_passphrase", self.ssid, self.psk],
                             stdout=subprocess.PIPE)
        p.wait()

        stdout = p.stdout.read()
        if p.returncode != 0:
            raise Exception(
                "wpa_passphrase returned {} ({})".format(p.returncode, stdout.decode()))

        with open(config_path, "w") as config_file:
            config = stdout.decode().splitlines()
            config.insert(0, "ap_scan=1")

            config.insert(-1, "	ampdu_factor=0")
            config.insert(-1, "	ampdu_density=0")
            config.insert(-1, "	disable_max_amsdu=1")
            config.insert(-1, "	disable_ht=1")
            config.insert(-1, "	disable_ht40=1")
            config.insert(-1, "	bgscan=\"\"")

            config_file.write("\n".join(config))
            config_file.write("\n")
            config_file.flush()

        return config_path


class WiFiConnectionError(Exception):
    """Exception for non-successful WiFi connections."""


class WiFiManager:
    """A Class to manage WiFi connections."""

    def __init__(self, interface="wlan0"):
        """
        Args:
            interface (str): WiFi interface to be managed
        """

        self.interface = interface

        self._lock = threading.Lock()
        self.wpa_supplicant = None
        self._start_ap()

    def _start_ap(self):
        if self.wpa_supplicant is not None:
            logger.info("don't starting ap; a wpa_supplicant is running")
        else:
            p = subprocess.Popen(["ifup", "-v", self.interface])
            p.wait(30)
            if p.returncode not in [0]:
                logger.warn("WiFi could not be restored, ignoring")

    def _stop_ap(self):
        p = subprocess.Popen(["ifdown", "-v", self.interface])
        p.wait(30)
        if p.returncode not in [0]:
            logger.warn("WiFi could not be stopped, ignoring")

    def connect(self, wifi, timeout=30):
        """Connect to WiFi.

        Args:
            wifi (WiFi): WiFi to connect to
            timeout (int): timeout for dhclient
        """

        logger.debug("acquire wifi access")
        self._lock.acquire()

        logger.info("connecting to wifi '{}'".format(wifi.ssid))
        if self.wpa_supplicant != None:
            self.disconnect()

        self._stop_ap()

        config_path = wifi._generate_config()
        wpa_cmd = ["wpa_supplicant", "-d", "-c",
                   config_path, "-i", self.interface]

        logger.debug("running {}".format(" ".join(wpa_cmd)))
        self.wpa_supplicant = subprocess.Popen(wpa_cmd)

        p = subprocess.Popen(["dhclient", "-v", self.interface])
        p.wait(timeout)
        if p.returncode not in [0]:
            self.wpa_supplicant.kill()
            self.wpa_supplicant = None

            self._start_ap()

            logger.debug("release wifi access")
            self._lock.release()

            logger.error("wifi connection failed.")
            raise WiFiConnectionError("dhclient failed")

    def disconnect(self):
        """Disconnect from current WiFi"""

        logger.info("disconnecting wifi")
        p = subprocess.Popen(["dhclient", "-v", "-r", self.interface])
        p.wait(30)
        if p.returncode not in [0]:
            logger.warning("dhclient failed to relase, ignoring.")

        logger.debug("killing wpa_supplicant")
        self.wpa_supplicant.send_signal(signal.SIGINT)
        self.wpa_supplicant.wait()
        self.wpa_supplicant = None

        p = subprocess.Popen(["ifconfig", "-v", self.interface, "down"])
        p.wait(30)
        if p.returncode not in [0]:
            logger.warning("ifconfig failed to stop interface, ignoring.")

        logger.info("wifi disconnected")

        self._start_ap()
        logger.debug("release wifi access")
        self._lock.release()

    def _scan_wifi(self, timeout=30):
        p = subprocess.Popen(["iwlist", self.interface, "scan"])
        p.wait(30)
        if p.returncode not in [0]:
            logger.warning("iwlist scan failed, ignoring.")


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    logger.addHandler(handler)

    wifi = WiFi("nature40-liftsystem-88cc", "supersicher")

    mgr = WiFiManager()
    mgr.connect(wifi)

    import time
    time.sleep(5)

    mgr.disconnect()

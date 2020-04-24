import socket
import time
import logging
import threading

import RPi.GPIO as gpio

from sensorproxy.wifi import WiFi, WiFiManager, WiFiConnectionError

logger = logging.getLogger(__name__)


class _MovingException(Exception):
    """Exception: lift cannot move further in the requested direction."""
    pass


class LiftConnectionException(Exception):
    """Exception: failed lift connections."""
    pass


class Lift:
    """Class representing a lift and its configuration."""

    def __init__(
        self,
        mgr: WiFiManager,
        height: float,
        ssid: str,
        psk: str = "supersicher",
        hall_bottom_pin: int = 5,
        hall_top_pin: int = 6,
        ip: str = "192.168.3.254",
        port: int = 35037,
        update_interval_s: float = 0.05,
        timeout_s: float = 0.5,
        travel_margin_s=1.0,
        charging_indicator=None,
        charging_docking_retries: int = 3,
        charging_docking_delay_s: float = 3.0,
    ):
        """
        Args:
            mgr (WiFiManager): WiFi manager to be used to connect
            height (float): Highest point the lift can reach, used for calibration
            ssid (str): WiFi SSID of the LiftSystem
            psk (str): WiFi pre-shared key of the LiftSystem
            hall_bottom_pin (int): GPIO pin of the bottom hall sensor
            hall_top_pin (int): GPIO pin of the top hall sensor
            ip (str): IP address of the LiftSystem
            port (int): server port of the LiftSystem
            update_interval_s (float): interval between lift speed updates
            timeout_s (float): speed commands timeout configured on the LiftSystem

        Examples:
            The lift can be instanciated without a WiFi configured, leaving the 
            WiFi configuration untouched. In the example the lift calibrates 
            itself, moving to the bottom, then to the top and back to the bottom 
            to measure the travel time. 

            >>> l = Lift(None, 12.6, "nature40.liftsystem.1337")
            >>> l.calibrate()
        """

        if height <= 0.0:
            raise ValueError("Not a valid lift height ({} m)".format(height))

        # mandatory parameters
        self.mgr = mgr
        self.height = height
        self.wifi = WiFi(ssid, psk)

        # optional (defaultable parameters)
        self.hall_bottom_pin = hall_bottom_pin
        self.hall_top_pin = hall_top_pin
        self.ip = ip
        self.port = port
        self.update_interval_s = update_interval_s
        self.timeout_s = timeout_s
        self.travel_margin_s = travel_margin_s
        self.charging_indicator = charging_indicator
        self.charging_docking_retries = charging_docking_retries
        self.charging_docking_delay_s = charging_docking_delay_s

        # calibration variables
        self._time_up_s = None
        self._time_down_s = None
        self._current_height_m = None

        # runtime variables
        self._lock = threading.Lock()
        self._sock = None
        self._current_speed = None
        self._last_response_ts = None

        # gpio initialization
        gpio.setmode(gpio.BCM)
        gpio.setup(hall_bottom_pin, gpio.IN)
        gpio.setup(hall_top_pin, gpio.IN)

    def __repr__(self):
        return "Lift {}".format(self.wifi.ssid)

    def connect(self, timeout_s: float = 10):
        """Connect to the configured lift.

        Args:
            timeout (float): timeout for connection attempts

        Raises:
            LiftSocketCommunicationException: if no response from lift on initial connect
        """

        logger.debug("acquire lift access")
        self._lock.acquire()

        if self.mgr:
            logger.info("connecting to '{}'".format(self.wifi.ssid))
            try:
                self.mgr.connect(self.wifi)
            except WiFiConnectionError as e:
                self._lock.release()
                raise e
        else:
            logger.info("wifi is handled externally")

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setblocking(False)

        start_ts = time.time()
        while self._recv_responses() == None:
            self._send_timeout(self.timeout_s)
            if start_ts + timeout_s < time.time():
                self.disconnect()
                raise LiftConnectionException(
                    "No response in {}s from lift in initial connect".format(timeout_s))

            time.sleep(self.update_interval_s)

        logger.info("connection to '{}' established".format(self.wifi.ssid))

    def disconnect(self):
        """Disconnect from the configured lift.
        """

        logger.info("disconnecting from lift")
        self._sock.close()
        self._sock = None

        if self.mgr:
            self.mgr.disconnect()

        logger.debug("release lift access.")
        self._lock.release()

    @property
    def hall_bottom(self):
        """Value of the bottom hall sensor."""
        _hall_bottom = gpio.input(self.hall_bottom_pin)
        return _hall_bottom

    @property
    def hall_top(self):
        """Value of the top hall sensor."""
        _hall_top = gpio.input(self.hall_top_pin)
        return _hall_top

    def _check_limits(self, speed: int):
        """Check if the lift can move in the requested direction.

        Args:
            speed (int): speed to be set

        Raises:
            MovingException: If the lift cannot move in the requested direction.
        """
        logger.debug(
            "Hall sensors top: {}, bottom: {}".format(self.hall_top, self.hall_bottom))

        if speed > 0 and self.hall_top:
            self._current_height_m = self.height
            raise _MovingException("lift cannot move upwards, reached sensor.")

        if speed < 0 and self.hall_bottom:
            self._current_height_m = 0.0
            raise _MovingException(
                "lift cannot move downwards, reached sensor.")

    def _check_timeout(self):
        """Check if the lift has timed out.

        Raises:
            LiftConnectionException: If the lift did not respond in time.
        """

        if self._last_response_ts is None:
            return

        delay = time.time() - self._last_response_ts
        if delay > self.timeout_s:
            raise LiftConnectionException(
                "No response from lift since {} s.".format(delay))

    def _send(self, cmd: str):
        """Send a command to the connected lift.

        Args:
            cmd (str): command to be send

        Raises:
            LiftConnectionException: If not connected to a lift.
        """

        if not self._sock:
            raise LiftConnectionException("Not connected to a lift")

        try:
            self._sock.sendto(cmd, (self.ip, self.port))
        except OSError as e:
            raise LiftConnectionException(
                "Sending to lift failed: {}".format(e))

    def _send_speed(self, speed: int):
        """Send a speed command to the connected lift.

        Args:
            speed (int): speed to be send
        """

        self._check_limits(speed)
        cmd = "speed {}".format(speed).encode()
        self._send(cmd)

    def _send_timeout(self, timeout_s: int):
        """Send a speed command to the connected lift.

        Args:
            timeout_s (int): timeout to be send in seconds
        """

        timeout_ms = (int)(timeout_s * 1000)
        cmd = "timeout {}".format(timeout_ms).encode()
        self._send(cmd)

    def _recv_responses(self):
        """Receive latest responses from the connected lift.

        Raises:
            LiftConnectionException: If not connected to a lift.
        """

        if not self._sock:
            raise LiftConnectionException("Not connected to a lift")

        argv = None

        while True:
            try:
                response = self._sock.recvfrom(65565)[0].decode()
                self._last_response_ts = time.time()
            except BlockingIOError:
                return argv

            logger.debug("received '{}'".format(response[:-1]))
            argv = response.split()

            if argv[0] == "speed":
                argv[1] = int(argv[1])
                self._current_speed = argv[1]
                logger.info("speed acknowledged: {}".format(
                    self._current_speed))
            elif argv[0] == "timeout":
                argv[1] = float(argv[1]) / 1000.0
                self.timeout_s = argv[1]
                logger.info("Timeout acknowledged: {}".format(
                    self.timeout_s))
            else:
                raise LiftConnectionException(
                    "Unknown Response from lift: '{}'".format(argv[0]))

    def _move(self, speed: int, moving_time_s: float = 300.0):
        """Move the lift for a period of time with a provided speed until the top or bottom is reached.

        Args:
            speed (int): speed to move the lift with, (-255, 255)
            time_s (float): period of time the lift shall move

        Returns:
            float: Time duration the lift moved.
        """

        logger.info(
            "moving lift with speed {} for max {}s".format(speed, moving_time_s))
        ride_start_ts = time.time()

        while True:
            next_loop_ts = time.time() + self.update_interval_s

            if ride_start_ts + moving_time_s < time.time():
                if speed == 0:
                    logger.info("Lift stopping finished.")
                else:
                    logger.info(
                        "Lift moved for {}s, stopping.".format(moving_time_s))
                break

            try:
                self._send_speed(speed)
                self._recv_responses()
                self._check_timeout()

            except LiftConnectionException as e:
                logger.warn("Lift command exception: {}".format(e))

            except _MovingException as e:
                logger.info("{}, stopping.".format(e))
                break

            sleep_s = next_loop_ts - time.time()
            if sleep_s > 0.0:
                time.sleep(sleep_s)

        ride_stop_ts = time.time()

        # send lift stop command (to be faster than timeout)
        if speed != 0:
            self._move(0, 1)

        self._last_response_ts = None
        return ride_stop_ts - ride_start_ts

    def move_to(self, height_request: float):
        if self._current_height_m == None:
            logger.warn("Lift is not calibrated yet, starting calibration!")
            self.calibrate()

        # location is already reached
        if self._current_height_m == height_request:
            logger.info("Lift is already at {}m.".format(height_request))
            return self._current_height_m

        # extremes: move all the way up or down
        if height_request >= self.height:
            logger.info("Requested height is high ({}m >= {}m maximum), moving to the top.".format(
                height_request, self.height))
            self._move(255, self._time_up_s + self.travel_margin_s)
            self._current_height_m = self.height
            return self._current_height_m

        if height_request <= 0.0:
            logger.info("Request height is low ({}m <= 0m), moving to the bottom.".format(
                height_request))
            self._move(-255, self._time_down_s + self.travel_margin_s)
            self.dock()

            self._current_height_m = 0.0
            return self._current_height_m

        # compute travel distance and duration
        travel_distance_m = height_request - self._current_height_m
        if travel_distance_m < 0:
            travel_speed_mps = - (self.height / self._time_down_s)
            motor_speed = -255
        else:
            travel_speed_mps = self.height / self._time_up_s
            motor_speed = 255

        travel_duration_s = travel_distance_m / travel_speed_mps

        # move the lift
        logger.info("Moving lift by {}m to reach {}m: moving {}s with speed {} m/s".format(
            travel_distance_m, height_request, travel_duration_s, travel_speed_mps))
        travel_duration_s = self._move(motor_speed, travel_duration_s)

        # set the reached height
        logger.debug("Reached height {}m after {}s".format(
            height_request, travel_duration_s))
        self._current_height_m = height_request

        # sanity-check reached height
        if self.hall_bottom:
            if self._current_height_m != 0.0:
                logger.error("Reached bottom hall sensor (0.0), but current height is {}, correcting.".format(
                    self._current_height_m))
        if self.hall_top:
            if self._current_height_m != self.height:
                logger.error("Reached top hall sensor ({}), but current height is {}, correcting.".format(
                    self.height, self._current_height_m))

        return self._current_height_m

    def dock(self):
        if self.charging_indicator == None:
            return

        for retry in range(self.charging_docking_retries):
            time.sleep(self.charging_docking_delay_s)

            is_charging = self.charging_indicator.record()[0][0]
            if is_charging:
                logger.info("Charging started.")
                return

            logger.info(
                "Charging did not start, retry docking ({}/{}).".format(retry+1, self.charging_docking_retries))
            self._move(255, 0.5)
            self._move(-255, 1)

    def calibrate(self):
        """Calibrate the lift travel times, by moving fully up and back down."""

        logger.info("Starting lift calibration program")
        logger.debug(
            "moving up (1 second steps) and back down to start in defined state.")
        while self.hall_bottom:
            self._move(255, 1)
        self._move(-255)

        logger.debug("moving lift to top")
        self._time_up_s = self._move(255)
        logger.debug("going back to bottom")
        self._time_down_s = self._move(-255)

        logger.info("calibration finished, {}s to the top, {}s back to bottom".format(
            self._time_up_s, self._time_down_s))

        travel_speed_up = self.height / self._time_up_s
        travel_speed_down = self.height / self._time_down_s
        logger.info(
            "lift speeds: {} m/s up, {} m/s down".format(travel_speed_up, travel_speed_down))

        self.dock()


if __name__ == "__main__":
    logger = logging.getLogger("pysensorproxy")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    mgr = None
    mgr = WiFiManager(interface="wlan0")

    lift = Lift(mgr=mgr, height=30, ssid="nature40-liftsystem-88cc")

    try:
        lift.connect()
        lift.calibrate()
        lift.disconnect()
    except LiftConnectionException as e:
        logger.error("Couldn't connect to lift: {}".format(e))

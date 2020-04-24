#!/usr/bin/env python3

import argparse
import datetime
import http.server
import json
import logging
import os
import platform
import socketserver
import threading
import time
import yaml
import subprocess
import sys

import schedule
from pytimeparse import parse as parse_time

import sensorproxy.sensors.audio
import sensorproxy.sensors.base
import sensorproxy.sensors.cellular
import sensorproxy.sensors.energy
import sensorproxy.sensors.environment
import sensorproxy.sensors.logger
import sensorproxy.sensors.optical
import sensorproxy.sensors.random
import sensorproxy.sensors.rsync
import sensorproxy.sensors.sink
import sensorproxy.sensors.system

from sensorproxy.lift import Lift
from sensorproxy.wifi import WiFiManager
from sensorproxy.influx import InfluxDBSensorClient

logger = logging.getLogger(__name__)


class ConfigurationException(Exception):
    pass


def run_threaded(job_func, *args):
    job_thread = threading.Thread(target=job_func, args=args)
    job_thread.start()


class SensorProxy:
    def __init__(self, config_path, metering_path, test=False):
        self.config_path = config_path

        logger.info("loading config file '{}'".format(config_path))
        with open(config_path) as config_file:
            config = yaml.load(config_file, Loader=yaml.Loader)

        system_time = time.time()
        config_mod_time = os.path.getmtime(config_path)

        if system_time < config_mod_time:
            logger.critical(
                "Current system time {} is before creation of the config file {}.".format(
                    system_time, config_mod_time))
            logger.critical(
                "Time travel is not yet available, so the system time seems to be wrong.")
            sys.exit("Wrong system time, aborting execution.")

        self._init_identifiers(**config)
        self._init_storage(**config)
        # self._init_local_log(**config)
        # the optionals has to be init first, as sensors depend on the existence of a lift
        self._init_optionals(**config)
        self._init_sensors(**config)

        logger.info("loading metering file '{}'".format(metering_path))
        with open(metering_path) as metering_file:
            self.meterings = yaml.load(metering_file, Loader=yaml.Loader)

        self._test_metering()

        if not test:
            self._reset_lift()

    def _init_identifiers(self, id: str = None, **kwargs):
        self.hostname = platform.node()
        if not id:
            raise ConfigurationException(
                "Configuration file is missing an ID for this instance.")

        blacklist = "/-."
        if any((c in set(blacklist)) for c in id):
            raise ConfigurationException(
                "The ID may not contain those characters: '{}'".format(blacklist))

        self.id = id
        logger.info("Running for id '{}' on host '{}'.".format(
            self.id, self.hostname))

    def _init_storage(self, storage_path=".", **kwargs):
        self.storage_path = storage_path
        try:
            os.makedirs(storage_path)
        except FileExistsError:
            pass

        self.storage_path_node = os.path.join(storage_path, self.hostname)
        try:
            os.makedirs(self.storage_path_node)
        except FileExistsError:
            pass

        logger.info("using storage at '{}'".format(storage_path))

    def _init_local_log(self, storage_path=".", log_level="INFO", **kwargs):
        if log_level.upper() not in logging._nameToLevel:
            logger.warn("log level '{}' is not in {}, defaulting to INFO".format(
                log_level, logging._nameToLevel.keys()))
            log_level = "INFO"

        log_level_num = logging._nameToLevel[log_level.upper()]
        log_path = os.path.join(
            storage_path, sensorproxy.sensors.base.Sensor.time_repr()+"_sensorproxy.txt")

        handler = logging.FileHandler(log_path, mode="w")
        handler.setLevel(log_level_num)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        app_logger = logging.getLogger("sensorproxy")
        app_logger.addHandler(handler)
        logger.info("local {} log is written to {}".format(
            log_level, log_path))

    def _init_optionals(self, wifi=None, lift=None, influx=None, **kwargs):
        self.wifi_mgr = None
        if wifi:
            self.wifi_mgr = WiFiManager(**wifi)
            logger.info("managing wifi '{}'".format(self.wifi_mgr.interface))

        self.lift = None
        if lift:
            try:
                self.lift = Lift(self.wifi_mgr, **lift)
                logger.info("using lift '{}'".format(self.lift.wifi.ssid))
            except Exception as e:
                logger.warn(
                    "lift initialization failed (lift not used): {}".format(e))

        self.influx = None
        if influx:
            self.influx = InfluxDBSensorClient(**influx)
            logger.info("using influx at '{}'".format(influx["host"]))

    def _init_sensors(self, sensors={}, **kwargs):
        self.sensors = {}
        for name, params in sensors.items():
            sensor_cls = sensorproxy.sensors.base.classes[params["type"]]
            sensor = sensor_cls(self, name, **params)
            self.sensors[name] = sensor

            logger.info("added sensor '{}' ({})".format(name, params["type"]))

            if isinstance(sensor, sensorproxy.sensors.energy.ChargingIndicator):
                if self.lift:
                    self.lift.charging_indicator = sensor

    def _reset_lift(self):
        if not self.lift:
            return

        try:
            self.lift.connect()
        except sensorproxy.wifi.WiFiConnectionError as e:
            logger.error("Couldn't connect to lift wifi: {}".format(e))
            return
        except sensorproxy.lift.LiftConnectionException as e:
            logger.error("Couldn't connect to lift: {}".format(e))
            return

        logger.info("Calibrating Lift")
        self.lift.calibrate()
        self.lift.disconnect()

    def test_interactive(self):
        self._test_hall_interactive()

    def _test_hall_interactive(self):
        if not self.lift:
            logger.info(
                "Interactive hall sensor test: no lift configured, skipping test."
            )
            return

        logger.info(
            "Interactive hall sensor test: approach with a magnet to trigger 1, remove magnet to trigger 0"
        )

        while self.lift.hall_bottom == 0:
            logger.warn(
                "Interactive hall sensor test (1/4):  bottom sensor reads 0, approach with a magnet..."
            )
            time.sleep(1)

        while self.lift.hall_bottom == 1:
            logger.warn(
                "Interactive hall sensor test (2/4): bottom sensor reads 1, remove magnet..."
            )
            time.sleep(1)

        while self.lift.hall_top == 0:
            logger.warn(
                "Interactive hall sensor test (3/4): top sensor reads 0, approach with a magnet..."
            )
            time.sleep(1)

        while self.lift.hall_top == 1:
            logger.warn(
                "Interactive hall sensor test (4/4): top sensor reads 1, remove magnet..."
            )
            time.sleep(1)

        logger.info("Interactive hall sensor test finished.")

    def _test_metering(self):
        for name, metering in self.meterings.items():
            logger.debug("Testing metering '{}'".format(name))
            self._run_metering(name, metering, test=True)

    def _run_metering(self, name, metering, test=False):
        logger.info("Running metering {}".format(name))

        if (not "heights" in metering) or (self.lift == None) or test:
            self._record_sensors_threaded(metering["sensors"], test=test)
        else:
            try:
                self.lift.connect()
                height_last = None

                for height_request in metering["heights"]:
                    height_reached = self.lift.move_to(height_request)
                    if height_last == height_reached:
                        logger.info("Last height ({}m) matches reached height ({}m), skipping metering. (requested: {}m, max: {}m)".format(
                            height_last, height_reached, height_request, self.lift.height))
                        continue

                    logger.info(
                        "Running metering {} at {}m.".format(name, height_reached))
                    self._record_sensors_threaded(
                        metering["sensors"], test=test)

                logger.info(
                    "Metering {} is done, moving back to bottom.".format(name))
                self.lift.move_to(0.0)
                self.lift.disconnect()

            except Exception as e:
                logger.error("Metering {} failed: {}".format(name, e))
                self._record_sensors_threaded(metering["sensors"], test=test)

    def _record_sensors_threaded(self, sensors: {str: dict}, test: bool):
        meter_threads = []
        height = self.lift._current_height_m if self.lift else None

        for name, params in sensors.items():
            sensor = self.sensors[name]
            t = threading.Thread(
                target=self._record_sensor, args=[sensor, params, test, height]
            )
            t.sensor = sensor
            meter_threads.append(t)
            t.start()

        for t in meter_threads:
            logger.debug("Waiting for {} to finish...".format(t.sensor.name))
            t.join()

    def _record_sensor(
        self,
        sensor: sensorproxy.sensors.base.Sensor,
        params: dict,
        test: bool,
        height_m: float,
    ):
        try:
            if test:
                params = params.copy()
                params["duration"] = "1s"
                params["count"] = 1
                params["delay"] = "0s"

            sensor.record(height_m=height_m, **params)
        except KeyError:
            logger.error(
                "Sensor '{}' is not defined in config: {}".format(
                    sensor.name, self.config_path
                )
            )
        except sensorproxy.sensors.base.SensorNotAvailableException as e:
            logger.error(
                "Sensor '{}' is not available: {}".format(sensor.name, e))

    def _schedule_metering(self, name: str, metering: dict):
        # default values for start and end (whole day)
        start = 0
        end = 24 * 60 * 60

        if "start" in metering["schedule"]:
            start = parse_time(metering["schedule"]["start"])
        if "end" in metering["schedule"]:
            end = parse_time(metering["schedule"]["end"])

        interval = parse_time(metering["schedule"]["interval"])

        logger.info(
            "metering '{}' from {} until {}, every {}".format(
                name, start, end, interval
            )
        )

        def schedule_day_second(day_second):
            ts = datetime.datetime.fromtimestamp(day_second)
            time = ts.time()

            s = schedule.every().day
            s.at_time = time
            s.do(run_threaded, self._run_metering, name, metering)

        if start < end:
            for day_second in range(start, end, interval):
                schedule_day_second(day_second)
        else:
            logger.info("metering {} runs over night (start: {}, end: {})".format(
                name, metering["schedule"]["start"], metering["schedule"]["end"]))
            # add one day to end
            end += 24 * 60 * 60

            for day_second in range(start, end, interval):
                # align day_second to the actual day
                day_second %= (60 * 60 * 24)
                schedule_day_second(day_second)

    def run(self):
        for name, metering in self.meterings.items():
            self._schedule_metering(name, metering)

        while True:
            schedule.run_pending()
            time.sleep(1)


def setup_logging(level):
    if level > 3:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.ERROR - (10 * level)

    # create stderr log
    stderr_formatter = logging.Formatter(
        "%(name)s - %(levelname)s - %(message)s")
    stderr_handler = logging.StreamHandler()
    stderr_handler.setFormatter(stderr_formatter)

    main_logger = logging.getLogger("sensorproxy")
    main_logger.addHandler(stderr_handler)
    main_logger.setLevel(logging_level)

    if level > 3:
        logger.warn("Logging level cannot be increased further.")


def main():
    parser = argparse.ArgumentParser(
        description="Read, log, safe and forward sensor readings."
    )
    parser.add_argument(
        "-c", "--config", help="config file (yml)", default="/boot/sensorproxy.yml"
    )
    parser.add_argument(
        "-m",
        "--metering",
        help="metering protocol (yml)",
        default="/boot/meterings.yml",
    )
    parser.add_argument(
        "-v", "--verbose", help="verbose output", action="count", default=0
    )
    parser.add_argument(
        "-t",
        "--test",
        help="only test if sensors are working",
        action="store_const",
        const=True,
        default=False,
    )
    args = parser.parse_args()

    setup_logging(args.verbose)
    proxy = SensorProxy(args.config, args.metering, args.test)

    if args.test:
        proxy.test_interactive()
        logger.info("Testing finished")
        return

    os.chdir(proxy.storage_path)
    proxy.run()


if __name__ == "__main__":
    p = subprocess.Popen(["pgrep", "sensorproxy"], stdout=subprocess.PIPE)
    status = p.wait()
    if status == 0:
        pids = p.stdout.read().decode().splitlines()
        logger.error("Sensorproxy already running, pid: {}".format(
            ", ".join(pids)))
        sys.exit(1)

    main()

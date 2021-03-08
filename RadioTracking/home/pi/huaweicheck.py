#!/usr/bin/env python3

import glob
import os
import logging
import subprocess


def match_usb_manuf(target):
    return [os.path.split(p)[0] for p in glob.glob("/sys/bus/usb/devices/*/manufacturer") if target in open(p).read()]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    target = "HUAWEI_MOBILE"
    ping_target = "8.8.8.8"
    huawei_paths = [os.path.split(p)[1].split(".") for p in match_usb_manuf(target)]

    logging.info(f"Found '{target}' devices at {huawei_paths}")

    logging.info(f"Running ping test for {ping_target}")
    p = subprocess.Popen(["ping", ping_target, "-c", "1"])
    p.wait()
    if not p.returncode:
        logging.info("Ping test succeeded, exiting.")
        exit(0)

    logging.warning(f"Ping test failed ({p.returncode}), cycling {target} device.")
    for location, port in huawei_paths:
        p = subprocess.Popen(["uhubctl", "--location", location, "--ports", port, "--action", "2"])
        p.wait()
        if p.returncode:
            logging.warning(f"Device {location}.{port} cycling failed ({p.returncode}), please check")

    logging.info("Finished.")

#!/usr/bin/env python3

import socket
import time

import RPi.GPIO as gpio

class Lift:
    def __init__(self, ip="192.168.4.1", port=35037):
        self.ip = ip
        self.port = port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def move(self, speed):
        payload = "{}".format(speed).encode("ascii")
        self.socket.sendto(payload, (self.ip, self.port))


# setup hall sensor
PIN_HALL = 26
gpio.setmode(gpio.BCM)
gpio.setup(PIN_HALL, gpio.IN)

lift = Lift()

while not gpio.input(PIN_HALL):
    print("Moving up")
    lift.move(255)
    time.sleep(0.2)


print("Stopping lift")
lift.move(0)
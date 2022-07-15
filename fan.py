#!/usr/bin/python3

import RPi.GPIO as GPIO
import time

channel = 14
sleeptime = 5
# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.OUT)

def motor_on(pin):
    GPIO.output(pin, GPIO.HIGH)  # Turn motor on


def motor_off(pin):
    GPIO.output(pin, GPIO.LOW)  # Turn motor off


if __name__ == '__main__':
    try:
        motor_on(channel)
        time.sleep(sleeptime)
        motor_off(channel)
        time.sleep(sleeptime)
        GPIO.cleanup()
    except KeyboardInterrupt:
        GPIO.cleanup()

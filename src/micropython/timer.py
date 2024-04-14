import time

import uasyncio
from gk import logging
from gk.fsm import State, StateMachine
from machine import Pin
import machine
from vl53l1x import VL53L1X


RED_LED = Pin(0, Pin.OUT, Pin.DRIVE_1)
GREEN_LED = Pin(1, Pin.OUT, Pin.DRIVE_0)
LASER_PIN = Pin(2, Pin.IN)


logging.enable()


class Init(State):
    async def enter(self):
        GREEN_LED.off()
        RED_LED.on()

    async def tick(self):
        return Calibrate()


class Calibrate(State):
    async def enter(self):
        distance = self.machine.distance

        range = distance.read()
        counts = 10
        await uasyncio.sleep_ms(100)

        pins = (RED_LED, GREEN_LED)
        while counts > 0:
            pins[0].off()
            pins[1].on()
            pins = (pins[1], pins[0])
            await uasyncio.sleep(0.5)

            curr_range = distance.read()
            diff = range - curr_range
            if abs(diff) <= 10:
                logging.log(logging.INFO, f"Range OK: {curr_range} [{diff}]")
                counts -= 1
            else:
                logging.log(logging.INFO, f"Range ERR: {curr_range} [{diff}]")
                counts = 10
                range = curr_range

        self.target_range = range

    async def tick(self):
        return Ready(self.target_range)


class Ready(State):
    def __init__(self, target_range):
        logging.log(logging.INFO, f"Target range: {target_range}")
        self.target_range = target_range

    async def enter(self):
        RED_LED.off()
        GREEN_LED.on()

    async def tick(self):
        await uasyncio.sleep_ms(1)
        range = self.machine.distance.read()
        if (range + 10) < self.target_range:
            return Lap(self.target_range, time.gmtime())


class Lap(State):
    def __init__(self, target_range, start_time):
        self.target_range = target_range
        self.start_time = start_time

    async def enter(self):
        RED_LED.on()
        GREEN_LED.on()
        await uasyncio.sleep(10)
        logging.log(logging.DEBUG, f"Debounce block ended")
        GREEN_LED.off()

    async def tick(self):
        await uasyncio.sleep_ms(1)
        range = self.machine.distance.read()
        if (range + 10) < self.target_range:
            return EndLap(self.start_time, time.gmtime())


class EndLap(State):
    def __init__(self, start_time, end_time):
        logging.log(logging.INFO, f"LAP: {start_time} {end_time}")

    async def tick(self):
        return Calibrate()


async def main():
    tasks = []

    try:
        i2c = machine.I2C(0, scl=Pin(9), sda=Pin(8))
        distance = VL53L1X(i2c)

        sm = StateMachine(
            i2c=i2c,
            distance=distance,
        )

        await sm.change(Init())

        while True:
            await sm.tick()

    finally:
        for task in tasks:
            task.cancel()


def run():
    uasyncio.run(main())

#run()

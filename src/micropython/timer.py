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
        counts = 10
        await uasyncio.sleep_ms(100)

        pins = (RED_LED, GREEN_LED)
        
        while counts > 0:
            pins[0].off()
            pins[1].on()
            pins = (pins[1], pins[0])
            await uasyncio.sleep(0.5)

            if LASER_PIN.value():
                counts -= 1
            else:
                logging.log(logging.WARN, "Calibration Reset")
                counts = 10

    async def tick(self):
        return Ready()


class Ready(State):
    def __init__(self):
        self.trigger = uasyncio.ThreadSafeFlag()
        self.start_time = None

    async def enter(self):
        RED_LED.off()
        GREEN_LED.on()

    async def tick(self):
        if LASER_PIN.value() == 0:
            start_time = time.ticks_ms()
            await uasyncio.sleep_ms(2)
            if LASER_PIN.value() == 0:
                return Lap(start_time)


class Lap(State):
    def __init__(self, start_time):
        self.start_time = start_time

    async def enter(self):
        RED_LED.on()
        GREEN_LED.on()
        await uasyncio.sleep(10)
        logging.log(logging.DEBUG, f"Debounce block ended")
        GREEN_LED.off()

    async def tick(self):
        value = LASER_PIN.value
        if value() == 0:
            end_time = time.ticks_ms()
            await uasyncio.sleep_ms(2)
            if value() == 0:
                return EndLap(self.start_time, end_time)


class EndLap(State):
    def __init__(self, start_time, end_time):
        duration = time.ticks_diff(end_time, start_time)
        logging.log(logging.INFO, f"LAP: {duration} (S:{start_time} E:{end_time})")

    async def tick(self):
        return Calibrate()


async def main():
    tasks = []

    try:
        #i2c = machine.I2C(0, scl=Pin(9), sda=Pin(8))
        #distance = VL53L1X(i2c)

        sm = StateMachine(
            #i2c=i2c,
            #distance=distance,
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

import time
import gc
import json
import net
import mqtt_as
import uasyncio
from gk import logging
from gk.fsm import State, StateMachine
from machine import Pin
import machine


RED_LED = Pin(0, Pin.OUT, Pin.DRIVE_1)
GREEN_LED = Pin(1, Pin.OUT, Pin.DRIVE_0)
LASER_PIN = Pin(2, Pin.IN)


logging.enable()


def message(mqtt, event, **kwargs):
    return mqtt.publish("gk-timer", json.dumps(dict(
        event=event,
        **kwargs
    )))


class Init(State):
    async def enter(self):
        bit = True
        RED_LED.on()
        GREEN_LED.on()

    async def tick(self):
        return Calibrate()


class Calibrate(State):
    async def enter(self):
        await message(self.machine.mqtt, 'calibrating')
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
        await message(self.machine.mqtt, 'ready')

    async def tick(self):
        if LASER_PIN.value() == 0:
            start_time = time.ticks_ms()
            await uasyncio.sleep_ms(2)
            if LASER_PIN.value() == 0:
                return Lap(start_time)


class Lap(State):
    def __init__(self, start_time):
        self.start_time = start_time
        self.ticker = None

    async def enter(self):
        RED_LED.on()
        GREEN_LED.on()
        #self.ticker = uasyncio.create_task(self.update())
        await message(self.machine.mqtt, 'lap_start', start_ticks=self.start_time)
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

    async def exit(self):
        #self.ticker.cancel()
        pass

    async def update(self):
        try:
            while True:
                await uasyncio.sleep(2)
                duration = time.ticks_diff(time.ticks_ms(), self.start_time)
                await message(self.machine.mqtt, "lap", start_ticks=self.start_time, duration=duration)
        except uasyncio.CancelledError:
            pass


class EndLap(State):
    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time
        self.duration = time.ticks_diff(end_time, start_time)
        logging.log(logging.INFO, f"LAP: {self.duration} (S:{start_time} E:{end_time})")

    async def enter(self):
        await message(self.machine.mqtt, 'lap_end', start_ticks=self.start_time, end_ticks=self.end_time, duration=self.duration)

    async def tick(self):
        return Calibrate()


async def main():
    tasks = []

    try:
        mqtt_as.MQTTClient.DEBUG = True
        mqtt = mqtt_as.MQTTClient(mqtt_as.config)
        await mqtt.connect()

        sm = StateMachine(
            mqtt=mqtt,
        )

        await sm.change(Init())

        while True:
            await sm.tick()

    finally:
        for task in tasks:
            task.cancel()


def run():
    net.configure_mqtt()
    gc.collect()

    uasyncio.run(main())

#run()

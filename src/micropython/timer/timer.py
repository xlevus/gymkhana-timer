import time
import gc
import json
import net
import sys
import mqtt_as
import logging
import uasyncio
from machine import Pin
import machine

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

RED_LED = Pin(0, Pin.OUT, Pin.DRIVE_1)
GREEN_LED = Pin(1, Pin.OUT, Pin.DRIVE_1)
BLUE_LED = Pin(2, Pin.OUT, Pin.DRIVE_1)

LASER_PIN = Pin(21, Pin.IN)


class Tripwire:
    def __init__(self, pin):
        self.pin = pin
        self.flag = uasyncio.ThreadSafeFlag()

    def tripped(self):
        return self.pin.value() == 0

    def set_irq(self):
        self.pin.irq(self._trigger)

    def _trigger(self, pin):
        self.flag.set()

    async def wait(self, ensure_ms=1):
        flag = self.flag
        while True:
            await flag.wait()
            trip_time = time.ticks_ms()
            flag.clear()

            await uasyncio.sleep_ms(ensure_ms)
            if self.tripped():
                return trip_time



def state(f):
    name = f.__name__
    async def _decorator(*args, **kwargs):
        logging.debug(f"Entering State {name}")
        return f(*args, **kwargs)
    return _decorator



async def message(mqtt, event, **kwargs):
    msg = json.dumps(dict(
        event=event,
        **kwargs
    )) 
    logging.debug(msg)
    uasyncio.create_task(mqtt.publish("gk-timer", msg, qos=0))
    return


@state
async def Init(t, mqtt):
    RED_LED.off()
    GREEN_LED.off()
    BLUE_LED.off()

    return Calibrate(t, mqtt)


@state
async def Calibrate(t, mqtt):
    await message(mqtt, 'calibrating')
    counts = 10
    await uasyncio.sleep_ms(100)

    pins = (RED_LED, GREEN_LED)
    
    while counts > 0:
        pins[0].off()
        pins[1].on()
        pins = (pins[1], pins[0])
        await uasyncio.sleep(0.5)

        if not t.tripped():
            counts -= 1
        else:
            logging.warning("Calibration Reset")
            counts = 10

    return Ready(t, mqtt)


@state
async def Ready(t, mqtt):
    RED_LED.off()
    GREEN_LED.on()
    await message(mqtt, 'ready')

    start_time = await t.wait()

    return Lap(t, mqtt, start_time)


async def lap_tick(mqtt, start_time):
    try:
        while True:
            await uasyncio.sleep(1.5)
            await message(mqtt, "lap", duration=time.ticks_diff(time.ticks_ms(), start_time))
    except uasyncio.CancelledError:
        logging.debug("Cancelled")
        pass


@state
async def Lap(t, mqtt, start_time):
    RED_LED.on()
    GREEN_LED.on()

    task = uasyncio.create_task(lap_tick(mqtt, start_time))

    await message(mqtt, 'lap_start', start_ticks=start_time)
    await uasyncio.sleep(10)
    logging.debug("Debounce block ended")
    GREEN_LED.off()

    end_time = await t.wait()

    task.cancel()
    return EndLap(t, mqtt, start_time, end_time)


@state
async def EndLap(t, mqtt, start_time, end_time):
    duration = time.ticks_diff(end_time, start_time)
    logging.info(f"LAP: {duration} (S:{start_time} E:{end_time})")

    await message(mqtt, 'lap_end', start_ticks=start_time, end_ticks=end_time, duration=duration)

    return Calibrate(t, mqtt)


async def statemachine(tripwire, mqtt):
    state = Init(tripwire, mqtt)

    while True:
        state = await state


async def up(mqtt):
    while True:
        await mqtt.up.wait()
        mqtt.up.clear()



async def main(mqtt):

    await mqtt.connect()
    gc.collect()

    tripwire = Tripwire(LASER_PIN)
    tripwire.set_irq()

    await uasyncio.gather(
        statemachine(tripwire, mqtt),
        #up(mqtt)
    )


def run():
    RED_LED.off()
    GREEN_LED.off()
    BLUE_LED.on()
    
    net.configure_mqtt()

    mqtt_as.MQTTClient.DEBUG = True
    mqtt_as.config['queue_len'] = 1
    mqtt = mqtt_as.MQTTClient(mqtt_as.config)

    uasyncio.run(main(mqtt))
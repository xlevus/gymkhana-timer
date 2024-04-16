import time
import random
import gc
import json
import net
import sys
import mqtt_as
import logging
import uasyncio
from machine import Pin
import machine
from display import DigitDisplay

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

RED_LED = Pin(0, Pin.OUT, Pin.DRIVE_1)
GREEN_LED = Pin(1, Pin.OUT, Pin.DRIVE_1)
BLUE_LED = Pin(2, Pin.OUT, Pin.DRIVE_1)

LASER_PIN = Pin(21, Pin.IN)

DISPLAY_SELECT = Pin(10, Pin.OUT)
SPI = machine.SPI(1, 10_000, sck=Pin(4), mosi=Pin(6), miso=Pin(5))

MAC = net.get_mac()


def rand_str():
    return "%s.%s" % (
        random.getrandbits(32),
        random.getrandbits(32),
    )


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
        device_id=MAC,
        **kwargs
    )) 
    logging.debug(msg)
    uasyncio.create_task(mqtt.publish("gk-timer", msg, qos=0))
    return


@state
async def Init(t, d, mqtt):
    RED_LED.off()
    GREEN_LED.off()
    BLUE_LED.off()
    d.write("STARTUP")

    return Calibrate(t, d, mqtt)


@state
async def Calibrate(t, d, mqtt):
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

    return Ready(t, d, mqtt)


@state
async def Ready(t, d, mqtt):
    RED_LED.off()
    GREEN_LED.on()
    lap_id = rand_str()
    await message(mqtt, 'ready', lap_id=lap_id)

    start_time = await t.wait()

    return Lap(t, mqtt, d, lap_id, start_time)


def ms_to_time(ms):
    return "%3d.%0.3d" % (ms // 1000,  ms % 1000)


async def _lap_tick(mqtt, lap_id, start_time):
    try:
        while True:
            await uasyncio.sleep(1.5)
            d = time.ticks_diff(time.ticks_ms(), start_time)
            await message(
                mqtt, "lap_tick", 
                lap_id=lap_id,
                duration_ms=d,
            )
    except uasyncio.CancelledError:
        pass


async def _timer_tick(d, start_time):
    try:
        while True:
            await uasyncio.sleep(0.213)
            duration=time.ticks_diff(time.ticks_ms(), start_time)
            d.write(ms_to_time(duration))
    except uasyncio.CancelledError:
        pass


@state
async def Lap(t, mqtt, d, lap_id, start_time):
    RED_LED.on()
    GREEN_LED.on()

    task = uasyncio.create_task(_lap_tick(mqtt, lap_id, start_time))
    task2 = uasyncio.create_task(_timer_tick(d, start_time))

    await message(mqtt, 'lap_start', lap_id=lap_id)
    d.write("START")
    await uasyncio.sleep(10)
    logging.debug("Debounce block ended")
    GREEN_LED.off()

    end_time = await t.wait()

    task.cancel()
    task2.cancel()
    return EndLap(t, mqtt, d, lap_id, start_time, end_time)


@state
async def EndLap(t, mqtt, d, lap_id, start_time, end_time):
    duration = time.ticks_diff(end_time, start_time)
    d.write(ms_to_time(duration))
    logging.info(f"LAP: {duration} (S:{start_time} E:{end_time})")

    await message(
        mqtt, 'lap_end', 
        lap_id=lap_id, 
        duration_ms=duration,
    )

    return Calibrate(t, d, mqtt)


async def statemachine(tripwire, display, mqtt):
    state = Init(tripwire, display, mqtt)

    while True:
        state = await state


async def up(mqtt):
    while True:
        await mqtt.up.wait()
        mqtt.up.clear()



async def main(mqtt):
    display = DigitDisplay(SPI, DISPLAY_SELECT)
    await display.init()
    await mqtt.connect()

    tripwire = Tripwire(LASER_PIN)
    tripwire.set_irq()
    
    gc.collect()

    try:
        await uasyncio.gather(
            statemachine(tripwire, display, mqtt),
            #up(mqtt)
        )
    except:
        display.write("ERR")
        raise


def run():
    RED_LED.off()
    GREEN_LED.off()
    BLUE_LED.on()
    
    mqtt_as.config['queue_len'] = 1
    mqtt_as.MQTTClient.DEBUG = True

    mqtt = net.configure_mqtt()

    uasyncio.run(main(mqtt))
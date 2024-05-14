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

from lidar.lidar import LIDAR

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

RED_LED = Pin(0, Pin.OUT, Pin.DRIVE_1)
GREEN_LED = Pin(1, Pin.OUT, Pin.DRIVE_1)
BLUE_LED = Pin(2, Pin.OUT, Pin.DRIVE_1)

LASER_PIN = Pin(21, Pin.IN)

DISPLAY_SELECT = Pin(10, Pin.OUT)
SPI = machine.SPI(1, 10_000, sck=Pin(4), mosi=Pin(6), miso=Pin(5))
I2C = machine.I2C(0, scl=Pin(9), sda=Pin(8))
LIDAR_ADDR = 0x10

MAC = net.get_mac()


def rand_str():
    return "%s.%s" % (
        random.getrandbits(32),
        random.getrandbits(32),
    )


def state(f):
    name = f.__name__
    def _decorator(*args, **kwargs):
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


class Tripwire:
    def __init__(self, pin):
        self.pin = pin
        self.flag = uasyncio.ThreadSafeFlag()

    def tripped(self):
        return self.pin.value() == 0

    def set_irq(self, trigger=Pin.IRQ_FALLING):
        self.pin.irq(self._trigger, trigger=trigger)

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



@state
async def Init(display, **_):
    RED_LED.off()
    GREEN_LED.off()
    BLUE_LED.off()
    display.write("BOOT")
    return InitLidar, (), {}


@state
async def InitLidar(**_):
    slaves = set()

    while LIDAR_ADDR not in slaves:
        slaves = I2C.scan()
        await uasyncio.sleep(0.5)

    lidar = LIDAR(I2C, LIDAR_ADDR)
    lidar.set_frequency(250)

    tripwire = Tripwire(LASER_PIN)

    return InitNet, (), {"lidar": lidar, "tripwire": tripwire}


@state
async def InitNet(display, **_):
    mqtt = net.configure_mqtt()
    
    if isinstance(mqtt, net.NullMQTT):
        display.write("NET ERR")
        await uasyncio.sleep(5)

    return Calibrate, (), {"mqtt": mqtt}


@state
async def Calibrate(lidar, mqtt, **_):
    await message(mqtt, 'calibrating')
    counts = 10
    await uasyncio.sleep_ms(100)

    pins = (RED_LED, GREEN_LED)

    distance = lidar.distance()
    
    while counts > 0:
        pins[0].off()
        pins[1].on()
        pins = (pins[1], pins[0])
        await uasyncio.sleep(0.5)

        new_distance = lidar.distance()
        logging.debug(f"Orig: {distance} New: {new_distance}")
        if abs(new_distance - distance) <= 5 and distance > 30:
            counts -= 1
        else:
            counts = 10
            distance = new_distance

    return Ready, (), {"trigger_distance": distance}


@state
async def Ready(mqtt, lidar: LIDAR, trigger_distance, **_):
    RED_LED.off()
    GREEN_LED.on()

    lap_id = rand_str()
    await message(mqtt, 'ready', lap_id=lap_id)

    while True:
        distance = lidar.distance()
        if (distance + 5) < trigger_distance:
            break
        await uasyncio.sleep_ms(1)

    start_time = time.ticks_ms()
    return Lap, (lap_id, start_time), {}


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
            await uasyncio.sleep(0.321)
            duration=time.ticks_diff(time.ticks_ms(), start_time)
            d.write(ms_to_time(duration))
    except uasyncio.CancelledError:
        pass


@state
async def Lap(lap_id, start_time, *, trigger_distance, lidar, mqtt, display, **_):
    RED_LED.on()
    GREEN_LED.on()

    task = uasyncio.create_task(_lap_tick(mqtt, lap_id, start_time))
    task2 = uasyncio.create_task(_timer_tick(display, start_time))

    try:

        await message(mqtt, 'lap_start', lap_id=lap_id)
        await uasyncio.sleep(10)
        logging.debug("Debounce block ended")
        GREEN_LED.off()

        while True:
            distance = lidar.distance()
            if (distance + 5) < trigger_distance:
                break

            await uasyncio.sleep_ms(1)


        await uasyncio.sleep(5)
        end_time = time.ticks_ms()

    finally:
        task.cancel()
        task2.cancel()

    return EndLap, (lap_id, start_time, end_time), {}


@state
async def EndLap(lap_id, start_time, end_time, *, display, mqtt, **_):
    duration = time.ticks_diff(end_time, start_time)
    display.write(ms_to_time(duration))
    logging.info(f"LAP: {duration} (S:{start_time} E:{end_time})")

    await message(
        mqtt, 'lap_end', 
        lap_id=lap_id, 
        duration_ms=duration,
    )

    return Calibrate, (), {}


async def statemachine(next_state, *args, **kwargs):
    state = next_state(*args, **kwargs)

    while True:
        next_state, args, new_kwargs = await state
        kwargs.update(new_kwargs)
        state = next_state(*args, **kwargs)



async def main():
    display = DigitDisplay(SPI, DISPLAY_SELECT)
    await display.init()
    
    gc.collect()

    try:
        await uasyncio.gather(
            statemachine(Init, display=display),
        )
    except:
        display.write("ERR")
        raise


def run():
    RED_LED.off()
    GREEN_LED.off()
    BLUE_LED.on()
    
    mqtt_as.MQTTClient.DEBUG = True
    mqtt_as.config['queue_len'] = 1

    uasyncio.run(main())
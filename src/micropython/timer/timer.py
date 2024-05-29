import time
import random
import gc
import sys
import logging
import uasyncio
import machine
from display import DigitDisplay
from tfluna import TfLuna

import net
from button import Button
from utils import rand_str, wait_first


logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

RED_LED = machine.Pin(0, machine.Pin.OUT, machine.Pin.DRIVE_1)
GREEN_LED = machine.Pin(1, machine.Pin.OUT, machine.Pin.DRIVE_1)
BLUE_LED = machine.Pin(2, machine.Pin.OUT, machine.Pin.DRIVE_1)

LIDAR_TRIGGER = machine.Pin(10, machine.Pin.IN)
LIDAR_UART = machine.UART(1, tx=8, rx=9, baudrate=115200)

DISPLAY_SELECT = machine.Pin(21, machine.Pin.OUT)
SPI = machine.SPI(1, 10_000, sck=machine.Pin(4), mosi=machine.Pin(6), miso=machine.Pin(5))

RESET_BUTTON = machine.Pin(20, machine.Pin.IN)

MAC = net.get_mac()


def state(f):
    name = f.__name__
    def _decorator(*args, **kwargs):
        logging.debug(f"Entering State {name}")
        return f(*args, **kwargs)
    return _decorator


@state
async def Init(**_):
    RED_LED.off()
    GREEN_LED.off()
    BLUE_LED.off()
    display = DigitDisplay(SPI, DISPLAY_SELECT)
    display.reset()
    display.write("Boot")

    reset = Button(RESET_BUTTON)
    reset.set_irq()

    await uasyncio.sleep(0.5)
    return InitLidar, (), {"display": display, "reset": reset}


@state
async def InitLidar(display, **_):
    display.write("LIDAR")

    lidar = TfLuna(LIDAR_UART)

    async with lidar:
        await lidar.soft_reset()
        await lidar.set_output_frequency(1)

        while lidar.distance is None:
            await uasyncio.sleep(0.1)
        
    tripwire = Button(LIDAR_TRIGGER)
    tripwire.set_irq(machine.Pin.IRQ_RISING)

    return InitNet, (), {"lidar": lidar, "tripwire": tripwire}


@state
async def InitNet(display, **_):
    mqtt = net.configure_mqtt()
    
    if isinstance(mqtt, net.NullMQTT):
        display.write("Net Err")
        await uasyncio.sleep(2)

    return Calibrate, (), {"mqtt": mqtt}


@state
async def Calibrate(lidar: TfLuna, display, mqtt, **_):
    await net.message(mqtt, 'calibrating')
    counts = 10

    async with lidar:
        await lidar.set_output_frequency(2)

        pins = (RED_LED, GREEN_LED)

        distance = lidar.distance
        
        while counts > 0:
            pins[0].off()
            pins[1].on()
            pins = (pins[1], pins[0])
            await uasyncio.sleep(0.5)

            new_distance = lidar.distance
            display.write(f"C. {new_distance}")
            logging.debug(f"Orig: {distance} New: {new_distance}")
            if abs(new_distance - distance) <= 5 and distance > 30:
                counts -= 1
            else:
                counts = 10
                display.write("Error")
                distance = new_distance

        await lidar.irq_mode(lidar.IRQ_MODE_HIGH, distance - 10, 5, 1, 10)
        await lidar.set_output_frequency(100)

    return Ready, (), {}


@state
async def Ready(mqtt, lidar: TfLuna, tripwire: Button, display, **_):
    RED_LED.off()
    GREEN_LED.on()

    lap_id = rand_str()
    await net.message(mqtt, 'ready', lap_id=lap_id)
    display.write('')

    start_time = await tripwire.wait()
    return Lap, (lap_id, start_time), {}


def ms_to_time(ms):
    return "%3d.%0.3d" % (ms // 1000,  ms % 1000)


async def _lap_tick(mqtt, lap_id, start_time):
    logging.debug("Lap Tick Start")
    try:
        while True:
            await uasyncio.sleep(1.5)
            d = time.ticks_diff(time.ticks_ms(), start_time)
            await net.message(
                mqtt, "lap_tick", 
                lap_id=lap_id,
                duration_ms=d,
            )
    except uasyncio.CancelledError:
        pass


async def _timer_tick(d, start_time):
    logging.debug("Timer Tick Start")
    try:
        while True:
            await uasyncio.sleep(random.uniform(0.1, 0.2))
            duration=time.ticks_diff(time.ticks_ms(), start_time)
            d.write(ms_to_time(duration))
    except uasyncio.CancelledError:
        pass


@state
async def Lap(lap_id, start_time, *, tripwire: Button, lidar, mqtt, display, reset: Button, **_):
    RED_LED.on()
    GREEN_LED.on()
    
    await net.message(mqtt, 'lap_start', lap_id=lap_id)

    task = uasyncio.create_task(_lap_tick(mqtt, lap_id, start_time))
    task2 = uasyncio.create_task(_timer_tick(display, start_time))

    try:
        await uasyncio.sleep(10)
        logging.debug("Debounce block ended")
        GREEN_LED.off()

        end_time = tripwire.wait()

        return EndLap, (lap_id, start_time, end_time), {}
    finally:
        task.cancel()
        task2.cancel()


@state
async def DNF(lap_id, *, display, mqtt, **_):
    display.write("DNF")
    await net.message(mqtt, "dnf", lap_id=lap_id)
    await uasyncio.sleep(5)
    return Calibrate, (), {}


@state
async def EndLap(lap_id, start_time, end_time, *, display, mqtt, **_):
    duration = time.ticks_diff(end_time, start_time)
    display.write(ms_to_time(duration))
    logging.info(f"LAP: {duration} (S:{start_time} E:{end_time})")

    await net.message(
        mqtt, 'lap_end', 
        lap_id=lap_id, 
        duration_ms=duration,
    )
    await uasyncio.sleep(10)

    return Calibrate, (), {}


async def statemachine(next_state, *args, **kwargs):
    state = next_state(*args, **kwargs)
    while True:
        next_state, args, new_kwargs = await state
        kwargs.update(new_kwargs)
        state = next_state(*args, **kwargs)
        gc.collect()


async def main():
    gc.collect()

    try:
        await uasyncio.gather(
            statemachine(Init),
        )
    except:
        raise


def run():
    RED_LED.off()
    GREEN_LED.off()
    BLUE_LED.off()

    uasyncio.run(main())
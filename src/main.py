import uasyncio
import time
from machine import Pin, SPI, ADC, Timer

from gk import logging
from gk.display import DigitDisplay
from gk.fsm import StateMachine, State

spi = SPI(1, baudrate=1_000_000)

display = DigitDisplay(
    spi,
    Pin(32, Pin.OUT),
)

LDR = Pin(35, Pin.IN)
LDR_ADC = ADC(LDR)
LDR_CLOSED_TH = 10000

GREEN_LED = Pin(22, Pin.OUT)
RED_LED = Pin(23, Pin.OUT)


logging.enable()


class Init(State):
    async def enter(self):
        await self.machine.display.init()
        await uasyncio.sleep_ms(5)
        await self.machine.display.init()

        GREEN_LED.off()
        RED_LED.on()

        display.write('coneheads')
        await uasyncio.sleep(5)

        await self.machine.change(Ready())

    async def tick(self):
        pass


def gate_closed():
    val = LDR_ADC.read_u16()
    return val < LDR_CLOSED_TH


def show_ms(display: DigitDisplay, ms: int):
    seconds = ms//1000
    millis = ms % 1000

    txt = "%3d.%0.3d" % (seconds, millis)
    display.write(txt)


class Ready(State):
    async def enter(self):
        GREEN_LED.on()
        RED_LED.off()
        show_ms(self.machine.display, 0)

    async def tick(self):
        if gate_closed():
            return TriggeredWait(time.ticks_ms())


class TriggeredWait(State):
    def __init__(self, start_ms):
        self.start_ms = start_ms

    async def enter(self):
        GREEN_LED.on()
        RED_LED.on()

    async def tick(self):
        curr_ms = time.ticks_ms()

        if  time.ticks_diff(curr_ms, self.start_ms) < 500:
            if gate_closed():
                pass
            else:
                return Ready()

        else:
            return Timing(self.start_ms)


class Timing(State):
    def __init__(self, start_ms):
        self.start_ms = start_ms

    async def enter(self):
        RED_LED.on()
        GREEN_LED.off()

    async def tick(self, curr_ms=None):
        curr_ms = curr_ms or time.ticks_ms()


        if gate_closed() and time.ticks_diff(curr_ms, self.start_ms) > 5000:
            return TimingEnd(self.start_ms, curr_ms)

        if curr_ms % 91 == 0:
            delta = time.ticks_diff(curr_ms, self.start_ms)
            show_ms(self.machine.display, delta)


class TimingEnd(State):
    def __init__(self, start_ms, end_ms):
        self.start_ms = start_ms
        self.end_ms = end_ms

    async def enter(self):
        RED_LED.on()
        GREEN_LED.on()

    async def tick(self):
        curr_ms = time.ticks_ms()

        if  time.ticks_diff(curr_ms, self.end_ms) < 500:
            if gate_closed():
                pass
            else:
                return EndTime(self.start_ms, self.end_ms)

        else:
            return Timing(self.start_ms)


class EndTime(State):
    def __init__(self, start_ms, end_ms):
        self.start_ms = start_ms
        self.end_ms = end_ms

    async def enter(self):
        RED_LED.off()
        GREEN_LED.off()
        show_ms(self.machine.display, time.ticks_diff(self.end_ms, self.start_ms))

    async def tick(self):
        curr_ms = time.ticks_ms()
        if time.ticks_diff(curr_ms, self.end_ms) > 60_000:
            return Ready()


async def main():
    tasks = []

    try:
        tasks.append(uasyncio.create_task(display.main()))

        machine = StateMachine(
            display=display,
        )

        await machine.change(Init())

        while True:
            await machine.tick()

    finally:
        for task in tasks:
            task.cancel()


def run():
    uasyncio.run(main())


run()
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


class Ready(State):
    async def enter(self):
        GREEN_LED.on()
        RED_LED.off()
        self.machine.display.write("0.00 000")

    async def tick(self):
        if gate_closed():
            return TriggeredWait(time.ticks_ms())


class TriggeredWait(State):
    def __init__(self, start_ms):
        self.start_ms = start_ms

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

    async def tick(self):
        curr_ms = time.ticks_ms()

        if curr_ms % 51 == 0:
            await self.update_display(curr_ms)

    async def update_display(self, curr_ms):
        delta = time.ticks_diff(curr_ms, self.start_ms)

        seconds = delta//1000
        ms = delta % 1000
        minutes = seconds // 60

        txt = "%1d.%0.2d %0.3d" % (minutes, seconds, ms)
        self.machine.display.write(txt)


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
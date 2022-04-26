import uasyncio
from machine import Pin, SPI, ADC, Timer

from gk import logging
from gk.display import DigitDisplay
from gk.fsm import StateMachine, State

spi = SPI(1, baudrate=50000)

display = DigitDisplay(
    spi,
    Pin(32, Pin.OUT),
)

LDR = Pin(35)
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

        await self.machine.change(Ready)

    async def tick(self):
        pass


class Ready(State):
    async def enter(self):
        GREEN_LED.on()
        RED_LED.off()
        self.machine.display.write("rdy...")

    async def tick(self):
        pass


async def main():
    tasks = []

    try:
        tasks.append(uasyncio.create_task(display.main()))

        machine = StateMachine(
            display=display,
        )

        await machine.change(Init)

        while True:
            await machine.tick()
            await uasyncio.sleep_ms(1)

    finally:
        for task in tasks:
            task.cancel()


def run():
    uasyncio.run(main())


run()
import uasyncio
from machine import Pin, SPI, ADC, Timer

from gk.display import DigitDisplay

spi = SPI(1, baudrate=50000)

display = DigitDisplay(
    spi,
    Pin(32, Pin.OUT),
)


async def main():
    tasks = []

    try:
        await display.init()
        await display.init()

        tasks.append(uasyncio.create_task(display.main()))

        display.write('coneheads')
        

        while True:
            await uasyncio.sleep(1)
    finally:
        for task in tasks:
            task.cancel()


def run():
    uasyncio.run(main())
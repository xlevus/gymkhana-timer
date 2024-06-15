import time
import asyncio
from machine import Pin


class Button:
    def __init__(self, pin):
        self.pin = pin
        self.flag = asyncio.ThreadSafeFlag()

    def tripped(self):
        return self.pin.value() == 0

    def set_irq(self, trigger=Pin.IRQ_FALLING):
        self.pin.irq(self._trigger, trigger=trigger)

    def _trigger(self, pin):
        self.flag.set()

    async def wait(self):
        flag = self.flag
        flag.clear()

        await flag.wait()
        return time.ticks_ms()

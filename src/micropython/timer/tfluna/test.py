import asyncio
import machine
from .tfluna import TfLuna
    
import logging
logging.basicConfig(level=logging.DEBUG)


async def _live_test(uart: machine.UART):
    tf = TfLuna(uart)

    async with tf:
        print("Version: ", await tf.get_version())
        await tf.set_output_frequency(100)

        await tf.irq_mode(tf.IRQ_MODE_HIGH, 60, 10, 10, 10)
        x = machine.Pin(10, machine.Pin.IN)

        while True:
            print(f"Distance: {tf.distance}  X:{x.value()}")
            await asyncio.sleep(1)


def live_test(uart):
    uart = uart or machine.UART(1, tx=8, rx=9, baudrate=115200)
    asyncio.run(_live_test(uart))
    return uart
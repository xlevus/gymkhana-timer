import logging
import uasyncio
import struct

logger = logging.getLogger(__name__)


class TfLuna:
    _CMD_HEADER = 0x5a
    _ID_GET_VERSION= 0x01
    _ID_SOFT_RESET = 0x02
    _ID_SAMPLE_FREQ = 0x03
    _ID_SAMPLE_TRIG = 0x04
    _ID_OUTPUT_ENABLE = 0x07
    _ID_RESTORE_DEFAULT = 0x10
    _ID_SAVE_SETTINGS = 0x11
    _ID_ON_OFF_MODE = 0x3B

    def __init__(self, uart):
        self._uart = uart
        self._sreader = uasyncio.StreamReader(self._uart)

        self.distance = None
        self.amplitude = None
        self.temp = None

        uasyncio.create_task(self._run())
        self._die = uasyncio.Event()

        self._cmdlock = uasyncio.Lock() 
        self._cmdset = uasyncio.Event()
        self._cmdresult = None

    async def _write(self, command: int, format: str, *values, resp_format=None):
        await self._cmdlock.acquire()
        try:
            self._cmdset.clear()
            msg = struct.pack(format+'x', *values)
            header = struct.pack("<bbb", self._CMD_HEADER, len(msg) + 3, command)
            await self._sreader.awrite(header+msg)
            if resp_format:
                logger.debug("Awaiting Response")
                await self._cmdset.wait()
                resp_command, *resp_data = self._cmdresult
                if resp_command != command:
                    logger.debug(f"Mismatched reply, {resp_command} expected {command}")
                    return None
                return struct.unpack(resp_format, self._cmdresult)
        finally:
            self._cmdlock.release()
            self._cmdresult = None

    async def _run(self):
        while not self._die.is_set():
            header = await self._sreader.read(2)

            if header is None:
                await uasyncio.sleep(0)
                continue

            elif header == b'YY':
                try:
                    self.distance, self.amplitude, temp = struct.unpack("<HHHx", await self._sreader.read(7))
                    self.temp = temp/8 - 256
                except ValueError:
                    pass

            elif header[0] == self._CMD_HEADER:
                data = await self._sreader.read(header[1] - 2)
                self._cmdresult = data
                self._cmdset.set()

            else:
                logger.debug(f"Wat? {header!r}")

        logger.debug("Run DIE")
    
    async def stop(self):
        self._die.set()

    async def output_enable(self, enable: bool = True):
        await self._write(
            self._ID_OUTPUT_ENABLE, '<b', enable
        )

    async def soft_reset(self):
        await self._write(self._ID_SOFT_RESET, "", wait_for_resp=False)

    async def set_output_frequency(self, frequency_hz: int):
        await self._write(self._ID_SAMPLE_FREQ, "<H", frequency_hz, resp_format="<bx")

    async def restore_defaults(self):
        await self._write(self._ID_RESTORE_DEFAULT, "")

    async def save_settings(self):
        await self._write(self._ID_SAVE_SETTINGS, "")

    IRQ_MODE_DISABLE = 0x00
    IRQ_MODE_HIGH = 0x01
    IRQ_MODE_LOW = 0x02
    async def irq_mode(self, mode: int, distance_cm: int, zone_cm: int, delay1_ms: int, delay2_ms: int):
        """Place TfLuna into "on/off" mode.
        This will set Pin6 high if something enters betwen it and `distance_cm` for `delay1_ms`, 
        and return it low if the object has moved `zone_cm` for a duration of `delay2_ms`.

        if IRQ_MODE_LOW is used, polarity of the trigger pin is reversed.

        NOTE: The IRQ pin will only ever trigger every one `output_frequency` cycle. Disabling
        the output or setting the output_frequency to 0 will disable the IRQ pin.
        """
        await self._write(
            self._ID_ON_OFF_MODE, "<BHHHH", 
            mode,
            distance_cm,
            zone_cm,
            delay1_ms,
            delay2_ms,
            resp_format="<bx"
        )

    async def trigger(self):
        await self._write(self._ID_SAMPLE_TRIG, "", wait_for_resp=False)

    async def get_version(self):
        return await self._write(self._ID_GET_VERSION, "", resp_format="<bbbx")


# if __name__ == '__main__':
#     tf = TfLuna(uart)
#     tf.soft_reset()
#     tf.output_enable(True)
#     tf.set_frequency(0)

async def _test(uart):
    tf = TfLuna(uart)

    await uasyncio.sleep(1)

    print("Version: ", await tf.get_version())
    await tf.set_output_frequency(100)

    await tf.irq_mode(tf.IRQ_MODE_HIGH, 60, 10, 10, 10)
    import machine
    x = machine.Pin(10, machine.Pin.IN)

    while True:
        print(f"Distance: {tf.distance}  X:{x.value()}")
        await uasyncio.sleep(1)


def test(uart):
    import logging
    logging.basicConfig(level=logging.DEBUG)
    import machine
    uart = uart or machine.UART(1, tx=8, rx=9, baudrate=115200)
    uasyncio.run(_test(uart))
    return uart
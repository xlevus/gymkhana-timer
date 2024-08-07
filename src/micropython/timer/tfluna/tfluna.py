import logging
import asyncio
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
        self._sreader = asyncio.StreamReader(self._uart)

        self.distance = None
        self.amplitude = None
        self.temp = None

        self._running = asyncio.Lock()
        self._ready = asyncio.Event()

        self._cmdlock = asyncio.Lock() 
        self._cmdset = asyncio.Event()
        self._cmdresult = None

    async def _write(self, command: int, format: str, *values, resp_format=None):
        if self._runtask is None:
            raise RuntimeError("Use inside a `async with TFLuna` block")

        await self._ready.wait()
        await self._cmdlock.acquire()
        try:
            self._cmdset.clear()
            msg = struct.pack(format+'x', *values)
            header = struct.pack("<bbb", self._CMD_HEADER, len(msg) + 3, command)
            await self._sreader.awrite(header+msg)
            if resp_format:
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
        try:
            self._ready.clear()
            while True:
                header = await self._sreader.read(2)

                if header is None:
                    await asyncio.sleep(0)
                    continue

                elif header == b'YY':
                    try:
                        self.distance, self.amplitude, temp = struct.unpack("<HHHx", await self._sreader.read(7))
                        self.temp = temp/8 - 256
                        self._ready.set()
                    except ValueError:
                        continue

                elif header[0] == self._CMD_HEADER:
                    data = await self._sreader.read(header[1] - 2)
                    self._cmdresult = data
                    self._cmdset.set()

                else:
                    logger.debug(f"Wat? {header!r}")
                    continue

                await asyncio.sleep(0)
        finally:
            return

    async def __aenter__(self):
        await self._running.acquire()
        self._runtask = asyncio.create_task(self._run())
    
    async def __aexit__(self, _, __, ___):
        self._runtask.cancel()
        self._runtask = None
        self._running.release()

    async def output_enable(self, enable: bool = True):
        await self._write(
            self._ID_OUTPUT_ENABLE, '<b', enable
        )

    async def soft_reset(self):
        logger.debug("Soft Reset")
        await self._write(self._ID_SOFT_RESET, "")

    async def set_output_frequency(self, frequency_hz: int):
        logger.debug(f"Setting Output Frequency to : {frequency_hz}")
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
        logger.debug(f"Entering IRQ Mode: {distance_cm}+={zone_cm} cm; {delay1_ms}/{delay2_ms} ms")
        resp = await self._write(
            self._ID_ON_OFF_MODE, "<BHHHH", 
            mode,
            distance_cm,
            zone_cm,
            delay1_ms,
            delay2_ms,
            resp_format="<bx"
        )
        logger.debug(f"IRQ: {resp!r}")

    async def trigger(self):
        await self._write(self._ID_SAMPLE_TRIG, "", wait_for_resp=False)

    async def get_version(self):
        return await self._write(self._ID_GET_VERSION, "", resp_format="<bbbx")
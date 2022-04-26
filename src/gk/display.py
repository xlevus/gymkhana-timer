# Library for MAX7219/MAX7221 SPI 8-digit LED Display Driver
# Part XC3714 from Jaycar.

import uasyncio

from . import logging

TEST_MODE = 0x0F
BRIGHTNESS = 0x0A
NO_DECODE = 0x09
SHUTDOWN = 0x0C
SCAN_LIMIT = 0x0B

DIGITS = {
    ' ': 0,
    '-': 1,
    '_': 8,
    '\'': 2,
    '0': 126,
    '1': 48,
    '2': 109,
    '3': 121,
    '4': 51,
    '5': 91,
    '6': 95,
    '7': 112,
    '8': 127,
    '9': 123,
    'a': 125,
    'b': 31,
    'c': 13,
    'd': 61,
    'e': 111,
    'f': 71,
    'g': 123,
    'h': 23,
    'i': 16,
    'j' : 24,
    # 'k' Can't represent
    'l': 6,
    # 'm' Can't represent
    'n': 21,
    'o': 29,
    'p': 103,
    'q': 115,
    'r': 5,
    's': 91,
    't': 15,
    'u': 28,
    'v': 28,
    # 'w' Can't represent
    # 'x' Can't represent
    'y': 59,
    'z': 109,
    'A': 119,
    'B': 127,
    'C': 78,
    'D': 126,
    'E': 79,
    'F': 71,
    'G': 94,
    'H': 55,
    'I': 48,
    'J': 56,
    # 'K' Can't represent
    'L': 14,
    # 'M' Can't represent
    'N': 118,
    'O': 126,
    'P': 103,
    'Q': 115,
    'R': 70,
    'S': 91,
    'T': 15,
    'U': 62,
    'V': 62,
    # 'W' Can't represent
    # 'X' Can't represent
    'Y': 59,
    'Z': 109,
    ',': 128,
    '.': 128,
    '!': 176,
}

SIZE = 8
LONG_PAD = 3

class DigitDisplay:
    def __init__(self, spi, pin):
        self.spi = spi
        self.pin = pin

        self.text = ''
        self.pointer = 0
        self.scroll = False

        self.task = None
        self.lock = uasyncio.Lock()

    def _write_register(self, register, value):
        self.pin.off();
        self.spi.write(bytearray([register, value]))
        self.pin.on()

    async def init(self):
        self.reset()
        await uasyncio.sleep(0.1)
        self.on()
        await uasyncio.sleep(0.1)
        self.write("X" * SIZE)
        await uasyncio.sleep(0.1)
        self.blank()
        await uasyncio.sleep(0.1)

    def on(self):
        self._write_register(SHUTDOWN, 1)

    def off(self):
        self._write_register(SHUTDOWN, 0)

    def reset(self):
        self._write_register(TEST_MODE, 0)
        self._write_register(BRIGHTNESS, 1)
        self._write_register(SCAN_LIMIT, 7)
        self.blank()
        self.on()

    def blank(self):
        self.scroll = False

        for i in range(0, SIZE):
            self._write_register(i + 1, 0)

    def write(self, text):
        logging.log(logging.DEBUG, text)
        self.pointer = 0
        if len(text) > SIZE:
            self.text = text + " " * LONG_PAD
            self.scroll = True
        else:
            self.text = '{:<8}'.format(text)
            self.scroll = False

        self.update()

    def update(self):
        text = ""
        for i in range(0, SIZE):
            text_pos = (self.pointer + i) % len(self.text)
            char = self.text[text_pos]
            symbol = DIGITS.get(char, 0)
            self._write_register(8 - i, symbol)
            text += char

        logging.log(logging.INFO, text)

    async def main(self):
        if self.lock.locked():
            return

        try:
            await self.lock.acquire()

            while True:
                if self.scroll:
                    self.update()
                    self.pointer += 1

                await uasyncio.sleep(0.5)
        finally:
            self.lock.release()

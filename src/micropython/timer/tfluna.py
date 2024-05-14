import struct


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

    _OUTPUT_DISTANCE = "dist"
    _OUTPUT_DATA = "data"
    _OUTPUT_UNKNOWN = "unkn"

    def __init__(self, uart):
        self._uart = uart
    def _read(self):
        pass
    def _write(self, command: int, format: str, *values):
        msg = struct.pack(format+'x', *values)
        header = struct.pack("<bbb", self._CMD_HEADER, len(msg) + 3, command)
        self._uart.write(header+msg)
    def _flush_buffer(self):
        while self._uart.read():
            pass
    def read(self):
        header = self._uart.read(2)
        if header is None:
            return None, None
        elif header == b'YY':
            distance, amplitude, temp = struct.unpack('<HHHx', self._uart.read(7))
            return self._OUTPUT_DISTANCE, {
                "distance_cm": distance,
                "amplitude": amplitude,
                "temp": temp/8 - 256,
            }
        elif header[0] == self._CMD_HEADER:
            data = self._uart.read(header[1] - 2)
            return self._OUTPUT_DATA, header+data
        else:
            return self._OUTPUT_UNKNOWN, header
    def output_enable(self, enable: bool = True):
        self._write(
            self._ID_OUTPUT_ENABLE, '<b', enable
        )
        if not enable:
            self._flush_buffer()
    def soft_reset(self):
        self._write(self._ID_SOFT_RESET, "")
    def set_output_frequency(self, frequency_hz: int):
        self._write(self._ID_SAMPLE_FREQ, "<H", frequency_hz)
        self._flush_buffer()
    def restore_defaults(self):
        self._write(self._ID_RESTORE_DEFAULT, "")
    def save_settings(self):
        self._write(self._ID_SAVE_SETTINGS, "")
    IRQ_MODE_DISABLE = 0x00
    IRQ_MODE_HIGH = 0x01
    IRQ_MODE_LOW = 0x02
    def irq_mode(self, mode: int, distance_cm: int, zone_cm: int, delay1_ms: int, delay2_ms: int):
        """Place TfLuna into "on/off" mode.
        This will set Pin6 high if something enters betwen it and `distance_cm` for `delay1_ms`, 
        and return it low if the object has moved `zone_cm` for a duration of `delay2_ms`.

        if IRQ_MODE_LOW is used, polarity of the trigger pin is reversed.

        NOTE: The IRQ pin will only ever trigger every one `output_frequency` cycle. Disabling
        the output or setting the output_frequency to 0 will disable the IRQ pin.
        """
        self._write(
            self._ID_ON_OFF_MODE, "<BHHHH", 
            mode,
            distance_cm,
            zone_cm,
            delay1_ms,
            delay2_ms
        )
    def trigger(self):
        self._write(self._ID_SAMPLE_TRIG, "")
    def distance(self):
        """Attempt to get the current distance."""
        self._flush_buffer()
        while True:
            type, value = self.read()
            if type == self._OUTPUT_DISTANCE:
                return value


tf = TfLuna(uart)
tf.soft_reset()
tf.output_enable(True)
tf.set_frequency(0)

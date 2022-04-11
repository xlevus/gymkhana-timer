import time
from machine import Pin, SPI, ADC, Timer

import fsm



# red_led = Pin(2, Pin.OUT, value=0)
# green_led = Pin(0, Pin.OUT, value=0)

# red_button = Pin(4, Pin.IN)
# green_button = Pin(5, Pin.IN)

# ldr = ADC(0)



# class Timer:
#     def __init__(self):
#         self.reset(None)

#         red_button.irq(trigger=Pin.IRQ_FALLING, handler=self.reset)
#         # green_button.irq(trigger=Pin.IRQ_FALLING, handler=self.start_timer)

#     def reset(self, pin):
#         self.timer_start = None
#         self.final_time = None
#         self.laser_blocked = None

#         green_led.value(1)
#         red_led.value(0)

#     def start_timer(self):
#         self.timer_start = time.ticks_ms()
#         self.timer_end = None
#         self.laser_blocked = True

#         green_led.value(0)
#         red_led.value(1)

#     def stop_timer(self, pin):
#         pass

#     def main(self):
#         count = 0

#         while True:
#             if self.timer_start:
#                 delta = time.ticks_diff(time.ticks_ms(), self.timer_start)
#                 if delta < 5000:
#                     continue

#             if ldr.read() < 400:
#                 count += 1
#             else:
#                 count = 0

#             if count >= 50:
#                 if not self.timer_start:
#                     self.start_timer()
#                 else:
#                     self.final_time = delta
#                     green_led.value(1)
#                     red_led.value(1)
#                     return

#     def display_tick(self):
#         pass

# t = Timer()
# t.main()

from display import DigitDisplay


GREEN_LED = Pin(22, Pin.OUT, value=0)

RED_LED = Pin(23, Pin.OUT, value=0)
RED_BTN = Pin(36, Pin.IN, Pin.PULL_UP)


class Init(fsm.State):
    def enter(self):
        self.machine.display.reset()


class Ready(fsm.State):
    def enter(self):
        self.machine.display.write('READY')
        GREEN_LED.on()


spi = SPI(1, baudrate=100000)


machine = fsm.StateMachine(
    Init,
    display=DigitDisplay(
        spi,
        Pin(32, Pin.OUT),
    )
)
PORT := "/dev/ttyACM0"
BAUD := "115200"

FIRMWARE := ESP32_GENERIC_C3-20240222-v1.22.2.bin"

.PHONY: repl

repl:
	picocom -b $(BAUD) $(PORT)

sync:
	mpy-sync --baud $(BAUD) --port $(PORT) --reset .

watch:
	mpy-watch --baud $(BAUD) --port $(PORT) --reset .

reset:
	mpy-reset --baud $(BAUD) --port $(PORT)

reflash:
	wget "https://micropython.org/resources/firmware/$(FIRMWARE)" -O "../../firmware/$(FIRMWARE)"
	esptool.py --chip esp32c3 --port $(PORT) erase_flash
	esptool.py --chip esp32c3 --port $(PORT) --baud 460800 write_flash -z 0x0 "$(FIRMWARE)"
	mpremote mip install logging
	mpremote mip install github:peterhinch/micropython-mqtt
PORT := "/dev/ttyACM0"
BAUD := "115200"

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
	esptool.py --chip esp32c3 --port $(PORT) erase_flash
	esptool.py --chip esp32c3 --port $(PORT) --baud 460800 write_flash -z 0x0 ../../firmware/ESP32_GENERIC_C3-20240222-v1.22.2.bin
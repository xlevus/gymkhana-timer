Gymkhana Timer
==============

Flashing
--------
1. Install dependencies
   ```bash
   pip install -r requirements-dev.txt
   ```
   
2. Set Environment
    ```bash
    export AMPY_PORT=/dev/ttyUSB0
    export AMPY_BAUD=115200
    ```

3. Flash ESP32 with esptool:
    ```bash
    esptool.py --chip esp32 --port $AMPY_PORT --baud 460800 write_flash -z 0x1000 firmware/esp32-20220117-v1.18.bin
    ```

4. Upload source:
    ```bash
    ./upload.sh
    ```

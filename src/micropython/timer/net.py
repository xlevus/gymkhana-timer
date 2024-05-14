import mqtt_as
import json
import network
import ubinascii

import logging


class NullMQTT:
    def __init__(self):
        logging.warning(f"Using NullMQTT")

    async def connect(self):
        pass

    async def publish(self, *_, **__):
        pass


def configure_mqtt():
    logging.debug("Configuring MQTT")

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    try:
        defined_networks = json.load(open("wifi.json", "r"))

        available_networks = {x[0].decode() for x in wlan.scan()}

        for row in defined_networks:
            if row['ssid'] in available_networks:
                logging.info(f"Connecting to network: {row['ssid']}")
                mqtt_as.config.update(row)
                return mqtt_as.MQTTClient(mqtt_as.config)
            else:
                logging.info(f"Could not find network: {row['ssid']}")

    except OSError:
        pass

    return NullMQTT()


def get_mac():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    return ubinascii.hexlify(wlan.config('mac')).decode()
    
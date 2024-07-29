import mqtt_as
import json
import network
import ubinascii
import asyncio

import logging

from utils import rand_str


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

    mqtt_as.MQTTClient.DEBUG = True
    mqtt_as.config['queue_len'] = 1

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


MAC = get_mac()


async def message(mqtt, event: str, *, qos: int=1, **kwargs):
    msg = json.dumps(dict(
        event=event,
        device_id=MAC,
        msgid=rand_str(),
        **kwargs
    )) 
    logging.debug(msg)
    asyncio.create_task(mqtt.publish("gk-timer", msg, qos=qos))
    return


import mqtt_as
import json
import network
import ubinascii


class NullMQTT:
    async def connect(self):
        pass

    async def publish(self, *_, **__):
        pass


def configure_mqtt():

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    try:
        defined_networks = json.load(open("wifi.json", "r"))

        available_networks = {x[0].decode() for x in wlan.scan()}

        for row in defined_networks:
            if row['ssid'] in available_networks:
                print(f"Network: {row['ssid']}")
                mqtt_as.config['ssid'] = row['ssid']
                mqtt_as.config['wifi_pw'] = row['key']
                mqtt_as.config['server'] = row['mqtt']
                return mqtt_as.MQTTClient(mqtt_as.config)

    except OSError:
        pass

    return NullMQTT()


def get_mac():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    return ubinascii.hexlify(wlan.config('mac')).decode()
    
import mqtt_as

def configure_mqtt():
    import network
    import json

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    try:
        defined_networks = json.load(open("wifi.json", "r"))
    except OSError:
        return None

    available_networks = {x[0].decode() for x in wlan.scan()}

    for row in defined_networks:
        if row['ssid'] in available_networks:
            print(f"Network: {row['ssid']}")
            mqtt_as.config['ssid'] = row['ssid']
            mqtt_as.config['wifi_pw'] = row['key']
            mqtt_as.config['server'] = row['mqtt']
            return

def do_connect():
    import network
    import json

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    try:
        defined_networks = json.load(open("wifi.json", "r"))
    except OSError:
        return None

    if not wlan.isconnected():
        available_networks = {x[0].decode() for x in wlan.scan()}
        print(available_networks)

        for row in defined_networks:
            print(row)
            if row['ssid'] in available_networks:
                wlan.connect(row['ssid'], row['key'])
                print('connecting to network...')

                while not wlan.isconnected():
                    pass

                return (wlan, row['mqtt'])

    else:
        ssid = wlan.config("ssid")
        for row in defined_networks:
            if row['ssid'] in available_networks:
                return (wlan, row['mqtt'])
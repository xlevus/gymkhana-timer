import network

NETWORKS = {
    "KTR": "3F@RedFoxes!"
}


def connect():
    sta_if = network.WLAN(STA_IF)
    sta_if.active(True)

    for row in sta_if.scan():
        ssid = row[0]
        ssid = ssid.decode()
        if ssid in NETWORKS:
            print("Connecting to network: " + ssid)
            sta_if.connect(ssid, NETWORKS[ssid])
            wlan.ifconfig()

            break


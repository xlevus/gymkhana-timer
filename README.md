# Gymkhana Timer

- [Gymkhana Timer](#gymkhana-timer)
  - [The Web App](#the-web-app)
    - [To Deploy](#to-deploy)
  - [The Hardware](#the-hardware)
    - [Flashing](#flashing)

## The Web App

Working instance can be found at [https://leaderboard.coneheads.org/](https://leaderboard.coneheads.org).

### To Deploy

```
$ ./pants package src/docker/web
$ flyctl deploy
```


## The Hardware

TBC.

### Flashing

1. Flash board with micropython
   ```bash
   cd src/micropython/timer
   make reflash
   ```
   
2. Upload source
  ```bash
  make sync
  ```

3. Edit wifi config
  ```
  mpremote edit wifi.json
  ```

  ```
  [
    {"ssid": "YOUR_SSID", "key": "WIFI PASSWORD", "mqtt": "mqtt.server.here"}
  ]
  ```
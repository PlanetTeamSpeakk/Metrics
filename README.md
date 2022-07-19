# Metrics
Source code of my metrics scripts for Grafana.

Instruments used:
- [Raspberry Pi 4B 4gb](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/) to run the scripts and power the instruments
- [Adafruit DHT22](https://www.adafruit.com/product/385) for temperature and humidity
- [Winsen MH-Z19C (with pins)](https://www.winsen-sensor.com/sensors/co2-sensor/mh-z19c.html) for carbon dioxide levels

# Why?
Honestly just because I could.  
The Pi is used for multiple things (like hosting some of my sites), not just metrics. The metrics, however, are mostly for fun.

# Creds
For obvious reasons, there are some secret constants in this project, these are stored in a file in the root directory named `creds.py` 
which looks like this:  
```py
DB_USER = "grafana-write"
DB_PASS = "password"
DB_HOST = "localhost"
DB_NAME = "grafana"

CF_API_KEY = "key" # CurseForge API key: https://console.curseforge.com/?#/api-keys

OWM_API_KEY = "key" # OpenWeatherMap API key: https://home.openweathermap.org/api_keys
LAT = "latitude" # Home latitude, from Google Maps
LON = "longitude" # Home longitude, from Google Maps
```

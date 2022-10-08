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

# Tables
Every module has its own table, so here's a table of all tables:  
| Module        | Table         | Query                                                                                                                                                                                                                                                                                                                                                                                                                                     |
|-------------- |-------------- |----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------   |
| CF Downloads  | cf_downloads  | `CREATE TABLE cf_downloads (time timestamp NOT NULL DEFAULT current_timestamp(), downloads int(11) DEFAULT NULL, KEY time (time))`                                                                                                                                                                                                                                                                                                        |
| CO2           | co2           | `CREATE TABLE co2 (time timestamp NOT NULL DEFAULT current_timestamp(), co2 int(11) NOT NULL, KEY time (time))`                                                                                                                                                                                                                                                                                                                           |
| Humitemp      | humitemp      | `CREATE TABLE humitemp (time timestamp NOT NULL DEFAULT current_timestamp(), temperature float DEFAULT NULL, humidity float DEFAULT NULL, KEY time (time))`                                                                                                                                                                                                                                                                               |
| Pi Temp       | pi_temp       | `CREATE TABLE pi_temp (time timestamp NOT NULL DEFAULT current_timestamp(), temp float NOT NULL, KEY time (time))`                                                                                                                                                                                                                                                                                                                        |
| Weather       | weather       | `CREATE TABLE weather (time timestamp NOT NULL DEFAULT current_timestamp(), description text NOT NULL, temp float NOT NULL, feels_like float NOT NULL, temp_min float NOT NULL, temp_max float NOT NULL, pressure smallint(6) NOT NULL, humidity tinyint(4) NOT NULL, wind_speed float NOT NULL, wind_angle smallint(6) NOT NULL, clouds tinyint(4) NOT NULL, icon char(3) NOT NULL, sunrise timestamp NOT NULL, sunset timestamp NOT NULL, timezone smallint(6) NOT NULL, KEY time (time))`    |

import adafruit_dht
import board
import json

dht = adafruit_dht.DHT22(board.D18)

def setup(register, db):
    register("humitemp", 30, 5, read)

def read(c):
    temp = dht.temperature
    humi = dht.humidity
    c.execute("INSERT INTO humitemp (temperature, humidity) VALUES (%s, %s);", (temp, humi))

    return {"temp": temp, "humi": humi}

def on_reload():
    dht.exit()

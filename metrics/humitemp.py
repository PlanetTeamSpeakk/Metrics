import adafruit_dht
import board
import json

def setup(register, db):
    register("humitemp", 30, 5, read)

def init():
    global dht
    dht = adafruit_dht.DHT22(board.D18)

def read(c):
    temp = dht.temperature
    humi = dht.humidity
    c.execute("INSERT INTO humitemp (temperature, humidity) VALUES (%s, %s);", (temp, humi))

    return {"temp": temp, "humi": humi}

def on_reload():
    dht.exit()

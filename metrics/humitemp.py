import adafruit_dht
import board
import json

dht = adafruit_dht.DHT22(board.D18)
temp = 0

def setup(register, db):
    register("temperature", 30, 5, read_temp)
    register("humidity", 30, 5, read_humi)

def read_temp(c):
    global dht, temp
    temp = dht.temperature

    return temp

def read_humi(c):
    global dht, temp
    humi = dht.humidity
    c.execute("INSERT INTO humitemp (temperature, humidity) VALUES (%s, %s);", (temp, humi))

    return humi

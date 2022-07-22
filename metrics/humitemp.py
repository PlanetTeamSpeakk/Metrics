import adafruit_dht
import board
import json
from objects import MeasurableModule

class HumiTemp(MeasurableModule):
    def __init__(self):
        super().__init__("HumiTemp", 30, 5)
        self.dht = adafruit_dht.DHT22(board.D18)

    def setup(self):
        self.mregister("temperature", lambda m: m["temp"])
        self.mregister("humidity", lambda m: m["humi"])

    def measure(self):
        temp = self.dht.temperature
        humi = self.dht.humidity

        return {"temp": temp, "humi": humi}

    def read_temp(self, measurement):
        return measurement["temp"]

    def read_humi(self, measurement):
        return measurement["humi"]

    def insert(self, c, value):
        c.execute("INSERT INTO humitemp (temperature, humidity) VALUES (%s, %s);", (value["temp"], value["humi"]))

    def on_reload(self):
        self.dht.exit()

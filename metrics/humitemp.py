import adafruit_dht
import board
import json
from objects import MeasurableModule
from prometheus_client import Gauge

class HumiTemp(MeasurableModule):
    def __init__(self):
        super().__init__("HumiTemp", 30, 5)
        self.dht = adafruit_dht.DHT22(board.D18)
        self.temp_gauge = Gauge("temperature", "The temperature in my room in degrees Celsius")
        self.humi_gauge = Gauge("humidity", "The humidity in my room in percent")

    def setup(self):
        self.mregister("temperature", lambda m: m["temp"])
        self.mregister("humidity", lambda m: m["humi"])

    def measure(self):
        temp = self.dht.temperature
        humi = self.dht.humidity

        return {"temp": temp, "humi": humi}

    def set(self, value):
        self.temp_gauge.set(value["temp"])
        self.humi_gauge.set(value["humi"])

    def on_reload(self):
        self.dht.exit()

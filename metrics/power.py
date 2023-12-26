import requests
import time
from __main__ import creds
from objects import MeasurableModule
from prometheus_client import Gauge, Histogram

class Power(MeasurableModule):
    def __init__(self):
        super().__init__("Power", 15, 5)
        self.consumption_gauge = Gauge("power_consumption", "Current amount of power consumed by my setup in watts")
        self.total_histo = Histogram("power_consumed", "Amount of power consumed in kWh")
        self.last_measurement = time.time()

    def setup(self):
        self.mregister("power-consumption", lambda m: m["power"])
        self.mregister("total-consumed", lambda m: round(m["total"] / 1000 / 60, 3))

    def measure(self):
        data = requests.get(f"http://{creds.SHELLY_IP}/meter/0", headers={"Authorization": "Basic " + creds.SHELLY_AUTH}).json()
        if not data["is_valid"]:
            raise Exception("Data was not valid")

        return data

    def set(self, value):
        # We don't use the 'total' field in the response data because it resets upon power loss.
        used = value["power"] * ((time.time() - self.last_measurement) / 60 / 60) / 1000
        self.last_measurement = time.time()

        self.consumption_gauge.set(value["power"])
        self.total_histo.observe(used)

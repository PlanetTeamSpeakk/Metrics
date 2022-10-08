import requests
from __main__ import creds
from objects import MeasurableModule

class Power(MeasurableModule):
    def __init__(self):
        super().__init__("Power", 15, 5)

    def setup(self):
        self.mregister("power-consumption", lambda m: m["power"])
        self.mregister("total-consumed", lambda m: round(m["total"] / 1000 / 60, 3))

    def measure(self):
        data = requests.get(f"http://{creds.SHELLY_IP}/meter/0", headers={"Authorization": "Basic " + creds.SHELLY_AUTH}).json()
        if not data["is_valid"]:
            raise Exception("Data was not valid")

        return data

    def insert(self, c, value):
        c.execute("INSERT INTO power (power_use, total) VALUES (%s, %s);", (value["power"], value["total"]))

import requests
from __main__ import creds, db
from objects import MeasurableModule

class Power(MeasurableModule):
    def __init__(self):
        self.interval = 15
        super().__init__("Power", self.interval, 5)

        c = db.db.cursor()
        c.execute("SELECT MAX(used) FROM power;")
        self.used = c.fetchall()[0][0]

    def setup(self):
        self.mregister("power-consumption", lambda m: m["power"])
        self.mregister("total-consumed", lambda m: round(m["total"] / 1000 / 60, 3))

    def measure(self):
        data = requests.get(f"http://{creds.SHELLY_IP}/meter/0", headers={"Authorization": "Basic " + creds.SHELLY_AUTH}).json()
        if not data["is_valid"]:
            raise Exception("Data was not valid")

        return data

    def insert(self, c, value):
        # We don't use the 'total' field in the response data because it resets upon power loss.
        self.used += value["power"] * (self.interval / 60 / 60) / 1000
        c.execute("INSERT INTO power (power_use, used) VALUES (%s, %s);", (value["power"], self.used))

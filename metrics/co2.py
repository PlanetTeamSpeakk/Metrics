import mh_z19
from objects import Module, Metric

class CO2(Module):
    def __init__(self):
        super().__init__("CO2")

    def setup(self):
        self.register("co2", 15, 5, self.read, self.insert)

    def read(self):
        co2 = mh_z19.read_co2valueonly(True)
        return co2

    def insert(self, c, value):
        c.execute("INSERT INTO co2 (co2) VALUES (%s);", (value,))

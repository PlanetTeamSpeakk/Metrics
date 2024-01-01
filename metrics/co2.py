import mh_z19
from objects import Module, Metric
from prometheus_client import Gauge

class CO2(Module):
    def __init__(self):
        super().__init__("CO2")
        self.gauge = Gauge("co2", "The carbon dioxide levels in my room.")

    def setup(self):
        self.register("co2", 15, 5, self.read, self.set)

    def read(self):
        return mh_z19.read_co2valueonly()

    def set(self, value):
        self.gauge.set(value)

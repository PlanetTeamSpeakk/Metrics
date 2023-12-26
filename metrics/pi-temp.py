import subprocess
from objects import Module
from prometheus_client import Gauge

class PiTemp(Module):
    def __init__(self):
        super().__init__("Pi Temp")
        self.gauge = Gauge("pi_temp", "Temperature of my Raspberry Pi in degrees Celsius")

    def setup(self):
        self.register("pi-temp", 15, 5, self.read, self.set)

    def read(self):
        i = 5
        pi_temp = round(sum(float(subprocess.check_output("/opt/vc/bin/vcgencmd measure_temp && sleep 0.5", shell=True)[5:-3]) for x in range(i)) / i, 1)

        return pi_temp

    def set(self, value):
        self.gauge.set(value)

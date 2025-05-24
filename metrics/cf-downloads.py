import requests
import __main__
from objects import Module
from prometheus_client import Gauge

last_downloads = 0

class CFDownloads(Module):
    def __init__(self):
        super().__init__("CF downloads")
        self.last_downloads = {}
        self.gauge_mc = Gauge("cf_downloads", "Downloads of my MoreCommands mod on CurseForge.")
        self.gauge_jc = Gauge("jc_downloads", "Downloads of the JCraft mod on CurseForge.")
        self.gauge_ra = Gauge("ra_downloads", "Downloads of the Roundabout mod on CurseForge.")

    def setup(self):
        self.register("cf-downloads", 60 * 60, 5 * 60, self.read_mc, self.set_mc)
        self.register("jc-downloads", 60 * 60, 5 * 60, self.read_jc, self.set_jc)
        self.register("ra-downloads", 60 * 60, 5 * 60, self.read_ra, self.set_ra)

    def read_mc(self):
        return self.get_downloads("250823")

    def read_jc(self):
        return self.get_downloads("854974")

    def read_ra(self):
        return self.get_downloads("1115305")

    def get_downloads(self, mod_id):
        data = requests.get("https://api.curseforge.com/v1/mods/" + mod_id, \
            headers = {"Accept": "application/json", "x-api-key": __main__.creds.CF_API_KEY}).json()["data"]

        prev = self.last_downloads[mod_id] if mod_id in self.last_downloads else 0
        downloads = max(int(data["downloadCount"]), prev)

        if downloads > prev:
            self.last_downloads[mod_id] = downloads

        return downloads

    def set_mc(self, value):
        self.gauge_mc.set(value)

    def set_jc(self, value):
        self.gauge_jc.set(value)

    def set_ra(self, value):
        self.gauge_ra.set(value)

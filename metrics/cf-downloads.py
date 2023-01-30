import requests
import __main__
from objects import Module

last_downloads = 0

class CFDownloads(Module):
    def __init__(self):
        super().__init__("CF downloads")
        self.last_downloads = 0

    def setup(self):
        self.register("cf-downloads", 60 * 60, 5 * 60, self.read, self.insert)

    def read(self):
        data = requests.get("https://api.curseforge.com/v1/mods/250823", headers = {"Accept": "application/json", "x-api-key": __main__.creds.CF_API_KEY}).json()["data"]
        downloads = self.last_downloads = max(int(data["downloadCount"]), last_downloads)

        return downloads

    def insert(self, c, value):
        c.execute("INSERT INTO cf_downloads (downloads) VALUES (%s);", (value,))

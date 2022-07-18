import requests
import __main__

last_downloads = 0

def setup(register, db):
    register("cf-downloads", 20 * 60, 5 * 60, read)

def read(c):
    global last_downloads
    data = requests.get("https://api.curseforge.com/v1/mods/250823", headers = {"Accept": "application/json", "x-api-key": __main__.creds.CF_API_KEY}).json()["data"]
    downloads = last_downloads = max(int(data["downloadCount"]), last_downloads)
    c.execute("INSERT INTO cf_downloads (downloads) VALUES (%s);", (downloads,))

    return downloads

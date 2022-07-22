import requests
from datetime import datetime
from __main__ import creds
from objects import MeasurableModule

class Weather(MeasurableModule):
    def __init__(self):
        super().__init__("Weather", 15 * 60, 5 * 60)

    def setup(self):
        self.mregister("description", lambda w: w["weather"][0]["description"])
        self.mregister("temperature", lambda w: w["main"]["temp"])
        self.mregister("feels like", lambda w: w["main"]["feels_like"])
        self.mregister("min temp", lambda w: w["main"]["temp_min"])
        self.mregister("max temp", lambda w: w["main"]["temp_max"])
        self.mregister("pressure", lambda w: w["main"]["pressure"])
        self.mregister("humidity", lambda w: w["main"]["humidity"])
        self.mregister("speed", lambda w: w["wind"]["speed"])
        self.mregister("wind angle", lambda w: w["wind"]["deg"])
        self.mregister("cloudiness", lambda w: w["clouds"]["all"])
        self.mregister("weather icon", lambda w: w["weather"][0]["icon"])
        self.mregister("sunrise", lambda w: datetime.utcfromtimestamp(w["sys"]["sunrise"]))
        self.mregister("sunset", lambda w: datetime.utcfromtimestamp(w["sys"]["sunset"]))
        self.mregister("timezone", lambda w: w["timezone"])

    def measure(self):
        return requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={creds.LAT}&lon={creds.LON}&appid={creds.OWM_API_KEY}&units=metric").json()

    def insert(self, c, weather):
        main = weather["main"]
        c.execute("INSERT INTO weather (description, temp, feels_like, temp_min, temp_max, pressure, humidity, wind_speed, wind_angle, clouds, icon, sunrise, sunset, timezone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
            (weather["weather"][0]["description"],
            main["temp"], main["feels_like"], main["temp_min"], main["temp_max"], main["pressure"], main["humidity"],
            weather["wind"]["speed"], weather["wind"]["deg"],
            weather["clouds"]["all"], weather["weather"][0]["icon"],
            datetime.utcfromtimestamp(weather["sys"]["sunrise"]), datetime.utcfromtimestamp(weather["sys"]["sunset"]), weather["timezone"]))

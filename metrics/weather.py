import requests
from datetime import datetime
from __main__ import creds

def setup(register, db):
    register("weather", 15 * 60, 5 * 60, read)

def read(c):
    weather = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={creds.LAT}&lon={creds.LON}&appid={creds.OWM_API_KEY}&units=metric").json()
    main = weather["main"]
    c.execute("INSERT INTO weather (description, temp, feels_like, temp_min, temp_max, pressure, humidity, wind_speed, wind_angle, clouds, sunrise, sunset, timezone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
        (weather["weather"][0]["description"],
        main["temp"], main["feels_like"], main["temp_min"], main["temp_max"], main["pressure"], main["humidity"],
        weather["wind"]["speed"], weather["wind"]["deg"],
        weather["clouds"]["all"],
        datetime.utcfromtimestamp(weather["sys"]["sunrise"]), datetime.utcfromtimestamp(weather["sys"]["sunset"])), weather["timezone"])

    return weather

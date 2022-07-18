import time
import mysql.connector as mysql
import __main__

db = mysql.connect(host="localhost", user="root", password=__main__.creds.DB_PASS, database="grafana")
last_reconnect = time.time()

def check_reconnect():
    global last_reconnect
    if time.time() - last_reconnect >= 3600:
        db.reconnect()
        last_reconnect = time.time()

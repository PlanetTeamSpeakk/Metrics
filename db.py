import time
import mysql.connector as mysql
from __main__ import creds

db = mysql.connect(host=creds.DB_HOST, user=creds.DB_USER, password=creds.DB_PASS, database=creds.DB_NAME)
last_reconnect = time.time()

def check_reconnect():
    global last_reconnect
    if time.time() - last_reconnect >= 3600:
        db.reconnect()
        last_reconnect = time.time()

import subprocess

def setup(register, db):
    register("pi-temp", 30, 5, read)

def read(c):
    i = 5
    pi_temp = round(sum(float(subprocess.check_output("/opt/vc/bin/vcgencmd measure_temp", shell=True)[5:-3]) for x in range(i)) / i, 1)
    c.execute("INSERT INTO pi_temp (temp) VALUES (%s);", (pi_temp,))

    return pi_temp

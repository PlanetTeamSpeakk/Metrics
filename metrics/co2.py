import mh_z19

def setup(register, db):
    register("co2", 30, 5, read)

def read(c):
    co2 = mh_z19.read()["co2"]
    c.execute("INSERT INTO co2 (co2) VALUES (%s);", (co2,))

    return co2

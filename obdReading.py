import obd

#obd.logger.setLevel(obd.logging.DEBUG)
conn = obd.OBD("socket://localhost:35000", baudrate=38400, fast=False)

c = conn.query(obd.commands['SPEED'])
r = conn.query(obd.commands.RPM)

if not r.is_null():
    print(r.value.magnitude)
    print("RPM")

if not c.is_null():
    print(c.value.magnitude)
    print("Km/h")
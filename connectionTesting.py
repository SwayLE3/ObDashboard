import obd

#obd.logger.setLevel(obd.logging.DEBUG)


CONNEXIONS = [
    {"portstr": "/dev/rfcomm0", "baudrate": 38400},
    {"portstr": "COM4", "baudrate": 38400},
    {"portstr": "socket://localhost:35000", "baudrate": 38400, "fast": False},
]
def getConnection():
    for params in CONNEXIONS:
            print(f"Essai de {params['portstr']}...")
            conn = obd.OBD(**params)
            if conn.is_connected():
                print(f"Connecté sur {params['portstr']}")
                return conn
            conn.close()
    return None

conn = getConnection()
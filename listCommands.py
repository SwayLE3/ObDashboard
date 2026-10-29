import obd
from obd.OBDResponse import Status

from connectionTesting import getConnection

#obd.logger.setLevel(obd.logging.DEBUG)

# Commandes qui modifient l'état de la voiture : on ne les envoie jamais
EXCLUDED = {"CLEAR_DTC"}


def formatValue(value):
    if isinstance(value, Status):
        return f"MIL={'ON' if value.MIL else 'OFF'}, {value.DTC_count} code(s) défaut"
    if isinstance(value, (bytes, bytearray)):
        return value.decode(errors="replace")
    return value


def listCommands(conn):
    commands = sorted(conn.supported_commands, key=lambda c: (c.mode or 0, c.pid or 0, c.name))
    print(f"\nProtocole : {conn.protocol_name()}")
    print(f"{len(commands)} commandes supportées\n")

    for cmd in commands:
        mode = f"{cmd.mode:02X}" if cmd.mode is not None else "--"
        pid = f"{cmd.pid:02X}" if cmd.pid is not None else "--"

        if cmd.name in EXCLUDED:
            value = "(non envoyée)"
        else:
            r = conn.query(cmd)
            value = "pas de réponse" if r.is_null() else formatValue(r.value)

        print(f"[{mode} {pid}] {cmd.name:<28} {cmd.desc:<45} {value}")


if __name__ == "__main__":
    conn = getConnection()
    if conn is None:
        print("Aucune connexion OBD trouvée")
    else:
        listCommands(conn)
        conn.close()

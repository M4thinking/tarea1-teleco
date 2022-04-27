import time

from db import *
from hashlib import *

HEADER = 64
PORT = 6969
HOST = "127.0.0.1"
ADDR = (HOST, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"


# Lee mensaje usando nuestro estándar de header + mensaje
def read(conn):
    msg_len = conn.recv(HEADER).decode(FORMAT)
    if msg_len:
        msg_len = int(msg_len)
        msg = conn.recv(msg_len).decode(FORMAT)
        return msg


def start_operations(conn, name, rut, entrada_no_valida = 0):
    options = f"""  Hola {name.split()[0]}, en qué te podemos ayudar?.\n
            \t(1) Revisar atenciones anteriores
            \t(2) Reiniciar servicios
            \t(3) Contactar a un ejecutivo
            \t(4) Salir"""
    if entrada_no_valida == 0:
        conn.send(options.encode(FORMAT))
    respuesta = read(conn)

    if respuesta == '1':
        check_attentions(conn, rut)
    elif respuesta == '2':
        msg = reset_service(conn, rut, name)
        print(f"[SERVER] {msg}")
        conn.send(f"[ASISTENTE] {msg}".encode(FORMAT))
        start_operations(conn, name, rut, 1)
    elif respuesta == '3':
        print(contact_operator(conn, name, "SERVER"))
        conn.send(contact_operator(conn, name, "ASISTENTE").encode(FORMAT))
        start_operations(conn, name, rut, 1)
    elif respuesta == '4':
        print(server_exit(conn, name, "SERVER"))
        conn.send(server_exit(conn, name, "ASISTENTE").encode(FORMAT))
        start_operations(conn, name, rut, 1)
    else:
        conn.send("Entrada no válida".encode(FORMAT))
        start_operations(conn, name, rut, 1)
    return


def check_attentions(conn, rut):
    db = abrir_json("temp_db.json")
    db_cliente = db[rut]["atenciones"]
    options = "Usted tiene las siguiente solicitudes en curso:\n\n"

    i = 1
    for id in db_cliente:
        descripcion = db_cliente[id]["descripcion"]
        options += f"\t({i}) Solicitud {id}: {descripcion}\n"
        i += 1

    options += "\nElija cual quiere la solicitud."
    conn.send(options.encode(FORMAT))
    return 1


def reset_service(conn, rut, name):
    db = abrir_json("temp_db.json")
    requestID = sha256()
    requestID.update(str(time.time()).encode("utf-8"))
    crear_atencion(db, rut, int(requestID.hexdigest()[:10], 16) % (10 ** 8), "Reseteo de Servicios")
    actualizar_json("temp_db.json", db)
    return f"Reinicio Servicios Cliente {name}."


def contact_operator(conn, name, sys):
    operator = "Juan"
    return f"[{sys}] Cliente {name} redirigido a ejecutivo {operator}."


def server_exit(conn, name, sys):
    disconnect_command = ':' + DISCONNECT_MESSAGE
    conn.send(disconnect_command.encode(FORMAT))
    return f"[{sys}] Cliente {name} desconectado."


# Esta no nos sirve mucho
def process_input(name):
    options = f"""  Hola {name.split()[0]}, en qué te podemos ayudar?.\n
        \t(1) Revisar atenciones anteriores
        \t(2) Reiniciar servicios
        \t(3) Contactar a un ejecutivo
        \t(4) Salir
        """
    return options

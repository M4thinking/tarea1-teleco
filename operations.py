from db import *

HEADER = 64
PORT = 6969
HOST = "127.0.0.1"
ADDR = (HOST, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"


# Lee mensaje usando nuestro estandar de header + mensaje
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
        reset_service(conn, name)
    elif respuesta == '3':
        contact_operator(conn, name)
    elif respuesta == '4':
        server_exit(conn, name)
        return
    else:
        conn.send("Entrada no válida".encode(FORMAT))
        start_operations(conn, name, rut, 1)
        return

    start_operations(conn, name, rut)
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


def reset_service(conn, name):
    print(f"[SERVER] Reinicio Servicios Cliente {name}.")
    return 2


def contact_operator(conn, name):
    operator = "Juan"
    print(f"[SERVER] Cliente {name} redirigido a ejecutivo {operator}.")
    return 3


def server_exit(conn, name):
    disconnect_command = ':' + DISCONNECT_MESSAGE
    conn.send(disconnect_command.encode(FORMAT))
    print(f"[SERVER] Cliente {name} desconectado.")
    return 4


# Esta no nos sirve mucho
def process_input(name):
    options = f"""  Hola {name.split()[0]}, en qué te podemos ayudar?.\n
        \t(1) Revisar atenciones anteriores
        \t(2) Reiniciar servicios
        \t(3) Contactar a un ejecutivo
        \t(4) Salir
        """
    return options


import time
from db import *
from hashlib import *
from send_read import *

HEADER = 64
PORT = 6969
HOST = "127.0.0.1"
ADDR = (HOST, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
DB_PATH = "db.json"
EJECUTIVOS_PATH = "ejecutivos.json"
ayuda_comandos = """Estos son los comandos que puedes utilizar:\n
\t :AYUDA - Muestra lista de comandos.
\t :DESCONECTAR - Para terminar la conversación.
"""

cola_ejecutivos = []
msg_buffer = ("ejecutivo", "")
db_ejecutivos = abrir_json(EJECUTIVOS_PATH)


# Comienza el diálogo entre cliente-servidor
def start_operations(conn, name, rut, entrada_no_valida=0):
    options = f"""[ASISTENTE] Hola {name.split()[0]}, en qué te podemos ayudar?.\n
            \t(1) Revisar atenciones anteriores
            \t(2) Reiniciar servicios
            \t(3) Contactar a un ejecutivo
            \t(4) Salir"""
    if entrada_no_valida == 0:
        conn.send(options.encode(FORMAT))
    respuesta = read(conn)

    # Revisar historial de atenciones
    if respuesta == '1':
        check_attentions(conn, rut)

    # Reiniciar servicios
    elif respuesta == '2':
        msg = reset_service(conn, rut, name)
        print(f"[SERVER] {msg}")
        conn.send(f"[ASISTENTE] {msg}".encode(FORMAT))
        start_operations(conn, name, rut, 1)

    # Contactar con ejecutivo
    elif respuesta == '3':
        if len(cola_ejecutivos) == 0:
            conn.send("[ASISTENTE] No hay ejecutivos disponibles en este momento.".encode(FORMAT))
            start_operations(conn, name, rut, 1)
            return
        # Sacamos el siguiente ejecutivo de la cola
        ejecutivo, rut_e, conn_e = cola_ejecutivos.pop(0)
        # Llamamos a la conexión entre cliente-ejecutivo, indicando cuando comienza y termina en el server
        print(f"[SERVER] Cliente {name} redirigido a ejecutivo {ejecutivo}.")
        contact_operator(conn, name, conn_e, ejecutivo, rut_e)
        conn.send(f"[ASISTENTE] Se terminó la conexión con {ejecutivo}".encode(FORMAT))

        start_operations(conn, name, rut, 1)

    # Terminamos conexión entre cliente-servidor
    elif respuesta == '4':
        print(server_exit(conn, name, "SERVER"))
        conn.send(server_exit(conn, name, "ASISTENTE").encode(FORMAT))
        # No hacemos recursión a start_operations, terminando el ciclo

    # Entrada no válida
    else:
        conn.send("Entrada no válida".encode(FORMAT))
        start_operations(conn, name, rut, 1)

    return


# Consulta a la base de datos, enviando al cliente sus atenciones
def check_attentions(conn, rut):
    db = abrir_json(DB_PATH)
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
    db = abrir_json(DB_PATH)
    requestID = sha256()
    requestID.update(str(time.time()).encode("utf-8"))
    crear_atencion(db, rut, int(requestID.hexdigest()[:10], 16) % (10 ** 8), "Reseteo de Servicios")
    actualizar_json(DB_PATH, db)
    return f"Reinicio Servicios Cliente {name}."


# Maneja toda la conexión entre cliente y ejecutivo
def contact_operator(conn_c, cliente, conn_e, ejecutivo, rut_e):
    # Tomamos como ocupado al ejecutivo
    db_ejecutivos[rut_e]["disponible"] = 0
    actualizar_json(EJECUTIVOS_PATH, db_ejecutivos)

    send(conn_e, f"Conectando con {cliente}...")
    conn_c.send(f":Conectando con {ejecutivo}...".encode(FORMAT))

    # Flujo de mensajes entre ejecutivo-cliente es como un ping-pong
    while True:
        msg_ejecutivo = read(conn_e)
        # En caso de que el ejecutivo envie un comando lo manejamos como un caso especial
        if msg_ejecutivo[0] == ':':
            comando = msg_ejecutivo[1:]
            if comando.upper() == "DESCONECTAR":
                break
            elif comando.upper() == "AYUDA":
                send(conn_e, ayuda_comandos)
            else:
                send(conn_e, "Comando no reconocido, ingresa ':AYUDA' para ver la lista de comandos.")
            continue
        conn_c.send(f"[{ejecutivo.split()[0]}] {msg_ejecutivo}".encode(FORMAT))

        msg_cliente = read(conn_c)
        send(conn_e, f"[{cliente.split()[0]}] {msg_cliente}")

    # Dejamos al ejecutivo disponible, para que el thread deje de esperar
    db_ejecutivos[rut_e]["disponible"] = 1
    actualizar_json(EJECUTIVOS_PATH, db_ejecutivos)
    return


# Maneja el termino de la conexión entre cliente-servidor
def server_exit(conn, name, sys):
    disconnect_command = ':' + DISCONNECT_MESSAGE
    conn.send(disconnect_command.encode(FORMAT))    # Enviamos mensaje para desconectar cliente
    return f"[{sys}] Cliente {name} desconectado."


# Lógica del ejecutivo
def start_ejecutivo(conn, name, rut):
    cola_ejecutivos.append((name, rut, conn))
    connected = True
    send(conn, f":[ASISTENTE] Hola {name.split()[0]}, estamos esperando una nueva conexión.")

    # Esperamos a que se conecte alguien
    while connected:
        if (name, rut, conn) not in cola_ejecutivos:
            connected = False
        time.sleep(1)

    time.sleep(1)   # Esperamos a que se actualice la db de ejecutivos
    # Dejamos al thread esperando hasta el fin de conexión con cliente
    while db_ejecutivos[rut]["disponible"] == 0:
        time.sleep(1)

    # Al terminar conexión preguntamos si quiere seguir en linea
    send(conn, f"{name}, desea atender a un nuevo cliente? (y/n)")
    continuar = read(conn)

    if continuar[0].upper() == 'Y':  # Volvemos a llamar a start_ejecutivo
        start_ejecutivo(conn, name, rut)

    else:   # Terminamos conexion
        disconnect_command = ':' + DISCONNECT_MESSAGE
        send(conn, disconnect_command)
        return



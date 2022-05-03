import time
import re
from db import *
from hashlib import *
from send_read import *
from datetime import datetime
from nlp import interp

HEADER = 64
PORT = 6969
HOST = "127.0.0.1"
ADDR = (HOST, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
DB_PATH = "db.json"
EJECUTIVOS_PATH = "ejecutivos.json"
ayuda_comandos = """Estos son los comandos que puedes utilizar:\n
\t :ayuda - Muestra lista de comandos.
\t :desconectar - Para terminar la conversación.
\t :subject <descripción solicitud> . Agrega/cambia el asunto relacionado con la solicitud. 
\t :state [abierto|cerrado]. Cambia el estado de la solicitud.
\t :history <nuevo historial>. Agrega nuevos antecedentes a la solicitud.
\t :name <username>. Cambia el Nombre del Ejecutivo
\t :restart. Reinicia todos sus servicios.
"""

cola_ejecutivos = []
msg_buffer = ("ejecutivo", "")
db_ejecutivos = abrir_json(EJECUTIVOS_PATH)


# Comienza el diálogo entre cliente-servidor
def start_operations(conn, name, rut, print_options=0):
    options = f"""[ASISTENTE] Hola {name.split()[0]}, en qué te podemos ayudar?.\n
            \t(1) Revisar atenciones anteriores
            \t(2) Reiniciar servicios
            \t(3) Contactar a un ejecutivo
            \t(4) Salir"""

    if print_options == 0:
        conn.send(options.encode(FORMAT))
    respuesta = read(conn)
    if not respuesta.isnumeric():
        respuesta = interp(respuesta)
    

    # Revisar historial de atenciones
    if respuesta == '1':
        attentions_status = ":[ASISTENTE] " + check_attentions(conn, rut)
        conn.send(attentions_status.encode(FORMAT))
        return start_operations(conn, name, rut, 0)

    # Reiniciar servicios
    elif respuesta == '2':
        msg = reset_service(conn, rut, name)
        print(f"[SERVER] {msg}")
        conn.send(f"[ASISTENTE] {msg}".encode(FORMAT))

    # Contactar con ejecutivo
    elif respuesta == '3':
        if len(cola_ejecutivos) == 0:
            conn.send("[ASISTENTE] No hay ejecutivos disponibles en este momento.".encode(FORMAT))
        else:
            # Sacamos el siguiente ejecutivo de la cola
            ejecutivo, rut_e, conn_e = cola_ejecutivos.pop(0)
            # Llamamos a la conexión entre cliente-ejecutivo, indicando cuando comienza y termina en el server
            print(f"[SERVER] Cliente {name} redirigido a ejecutivo {ejecutivo}.")
            contact_operator(conn, name, rut, conn_e, ejecutivo, rut_e)
            conn.send(f"[ASISTENTE] Se terminó la conexión con {ejecutivo}".encode(FORMAT))

    # Terminamos conexión entre cliente-servidor
    elif respuesta == '4':
        print(server_exit(conn, name, "SERVER"))
        conn.send(server_exit(conn, name, "ASISTENTE").encode(FORMAT))
        return
        # No hacemos recursión a start_operations, terminando el ciclo

    # Entrada no válida
    else:
        conn.send("Entrada no válida".encode(FORMAT))

    return start_operations(conn, name, rut, 1)


# Consulta a la base de datos, enviando al cliente sus atenciones
def check_attentions(conn, rut):
    db = abrir_json(DB_PATH)
    db_cliente = db[rut]["atenciones"]

    if db_cliente == {}:
        return "No hay atenciones anteriores."

    options = "Usted tiene las siguiente solicitudes en curso:\n\n"

    i = 1

    for id in db_cliente:
        descripcion = db_cliente[id]["descripcion"]
        options += f"\t({i}) Solicitud {id}: {descripcion}\n"
        i += 1

    options += "\nElija cual solicitud quiere revisar."
    conn.send(options.encode(FORMAT))
    respuesta = read(conn)

    try:
        respuesta = int(respuesta)
    except (RuntimeError, TypeError, NameError, ValueError):
        return "Entrada inválida."

    if 0 < int(respuesta) < i:
        id_at_json = db[rut]["atenciones"].keys()
        id_request = [*id_at_json][respuesta - 1]
        db_historial = db[rut]["atenciones"][id_request]["historial"]

        if db_historial == {}:
            return "No hay historial asociado a esta solicitud."

        detalle = f"Historial de la solicitud {id_request}\n"
        for fecha in db_historial:
            detalle += f"\t Fecha {fecha}: {db_historial[fecha]}\n"

        return f"{detalle}"
    else:
        return "Entrada inválida."


def reset_service(conn, rut, name):
    db = abrir_json(DB_PATH)
    requestID = sha256()
    requestID.update(str(time.time()).encode("utf-8"))
    crear_atencion(db, rut, int(requestID.hexdigest()[:10], 16) % (10 ** 8), "Reseteo de Servicios")
    actualizar_json(DB_PATH, db)
    return f"Reinicio Servicios Cliente {name}."


# Maneja toda la conexión entre cliente y ejecutivo
def contact_operator(conn_c, cliente, rut, conn_e, ejecutivo, rut_e):
    # Tomamos como ocupado al ejecutivo
    db_ejecutivos[rut_e]["disponible"] = 0
    actualizar_json(EJECUTIVOS_PATH, db_ejecutivos)

    # Explicitamos la conexión
    send(conn_e, f"Conectando con {cliente}...")
    conn_c.send(f":Conectando con {ejecutivo}...".encode(FORMAT))

    # Por defecto se crea una solicitud de "Consulta con Ejecutivo."
    requestID = sha256()
    inicio_solicitud = datetime.now().strftime("%Y-%m-%d %H:%M")
    requestID.update(str(time.time()).encode("utf-8"))
    id_solicitud = int(requestID.hexdigest()[:10], 16) % (10 ** 8)

    # Conexión a la base de datos de los clientes e inserción de solicitud con historial
    db = abrir_json(DB_PATH)
    crear_atencion(db, rut, id_solicitud, "Comunicación con Ejecutivo.")
    crear_historial(db, rut, id_solicitud, inicio_solicitud, f"Contacto con {ejecutivo}, Rut: {rut_e}.".encode(FORMAT))
    actualizar_json(DB_PATH, db)

    # Flujo de mensajes entre ejecutivo-cliente es como un ping-pong
    while True:
        msg_ejecutivo = read(conn_e)
        # En caso de que el ejecutivo envie un comando lo manejamos como un caso especial
        if msg_ejecutivo[0] == ':':
            comando = msg_ejecutivo[1:]
            if re.match('desconectar', comando):
                break
            elif re.match('ayuda', comando):
                send(conn_e, ayuda_comandos)

            elif re.match('^subject ', comando):
                subject = comando.replace("subject ", "", 1)  # Borra el comando la primera vez que aparece

                if subject == "":
                    send(conn_e, f'Ingresa una descricpión válida.')
                    continue
                db = abrir_json(DB_PATH)
                modificar_descripcion(db, rut, id_solicitud, subject)
                actualizar_json(DB_PATH, db)
                send(conn_e, f'Cambio de descripción a "{subject}"')

            elif re.match('^state ', comando):
                state = comando.replace("state ", "", 1)  # Borra el comando la primera vez que aparece

                if re.match('abierto', state):
                    state = True
                elif re.match('cerrado', state):
                    state = False
                else:
                    send(conn_e, "Estado inválido, intentalo nuevamente.")
                    continue
                db = abrir_json(DB_PATH)
                modificar_estado(db, rut, id_solicitud, state)
                actualizar_json(DB_PATH, db)
                send(conn_e, f'Cambio de estado de solicitud a "{state}" realizado con éxito.')

            elif re.match('^history ', comando):
                historial = comando.replace("history ", "", 1) # Borra el comando la primera vez que aparece
                fecha_nuevo_historial = datetime.now().strftime("%Y-%m-%d %H:%M")
                db = abrir_json(DB_PATH)
                crear_historial(db, rut, id_solicitud, fecha_nuevo_historial, historial)
                actualizar_json(DB_PATH, db)
                send(conn_e, f'Nuevo detalle "{historial}" con fecha {fecha_nuevo_historial}.')

            elif re.match('^name ', comando):
                name = comando.replace("name ", "", 1)  # Borra el comando la primera vez que aparece
                db_ejecutivos[rut_e]["nombre"] = name
                actualizar_json(EJECUTIVOS_PATH, db_ejecutivos)
                send(conn_e, f'¡Hola de nuevo {name}!')

            elif re.match('restart', comando):
                fecha_reinicio = datetime.now().strftime("%Y-%m-%d %H:%M")
                db = abrir_json(DB_PATH)
                crear_historial(db, rut, id_solicitud, fecha_reinicio, "Reinicia todos sus servicios")
                actualizar_json(DB_PATH, db)
                send(conn_e, f'Reinicio de todos los servicios con fecha {fecha_reinicio}.')
            else:
                send(conn_e, "Comando no reconocido, ingresa ':ayuda' para ver la lista de comandos.")
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
    conn.send(disconnect_command.encode(FORMAT))  # Enviamos mensaje para desconectar cliente
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

    time.sleep(1)  # Esperamos a que se actualice la db de ejecutivos
    # Dejamos al thread esperando hasta el fin de conexión con cliente
    while db_ejecutivos[rut]["disponible"] == 0:
        time.sleep(1)

    # Al terminar conexión preguntamos si quiere seguir en linea
    send(conn, f"{name}, desea atender a un nuevo cliente? (y/n)")
    continuar = read(conn)

    if continuar[0].upper() == 'Y':  # Volvemos a llamar a start_ejecutivo
        start_ejecutivo(conn, name, rut)

    else:  # Terminamos conexion
        disconnect_command = ':' + DISCONNECT_MESSAGE
        send(conn, disconnect_command)
        return

import socket
import threading
from db import *
from send_read import send, read
from operations import DB_PATH, EJECUTIVOS_PATH, cola_ejecutivos, msg_buffer
import operations

HEADER = 64
PORT = 6969
HOST = "127.0.0.1"
# Consigue la ipv4 de la maquina donde se corre
# HOST = socket.gethostbyname(socket.gethostname())
ADDR = (HOST, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

# socket( familia = AF_INET para ipv6,  forma de enviar datos =  TCP/IP)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
db = abrir_json(DB_PATH)
db_ejecutivos = abrir_json(EJECUTIVOS_PATH)


# Corre en paralelo para cada cliente
def handle_client(conn, addr):
    print(f"[NUEVA CONEXIÓN] {addr} connected.")
    rut = read(conn)  # Recibimos el rut

    # Si no está en la base de datos le pedimos el nombre
    if rut not in db:
        conn.send("0".encode(FORMAT))  # Indicamos que no tiene nombre y lo recibimos
        name = read(conn)

        crear_cliente(db, rut, name)
        actualizar_json(DB_PATH, db)

    # Si ya esta en la base de datos sacamos su nombre y lo mandamos al cliente para que lo salude
    else:
        conn.send("1".encode(FORMAT))  # Indicamos al cliente que tenemos su nombre
        name = db[rut]["nombre"]

    print(f"[SERVER] Cliente {name} conectado.")

    # Comenzamos llamada desde operations
    operations.start_operations(conn, name, rut)

    # Cerramos la conexión
    conn.close()


def handle_ejecutivo(conn, addr):
    print(f"[NUEVA CONEXIÓN] Ejecutivo desde {addr} connected.")
    rut = read(conn)  # Recibimos el rut del ejecutivo

    # Si no esta en nuestra base de datos terminamos proceso
    if rut not in db_ejecutivos:
        print(f"[SERVER] {rut} no es ejecutivo.")
        conn.send("0".encode(FORMAT))  # informamos a ejecutivo.py que no hay registro
        conn.close()
        return

    conn.send("1".encode(FORMAT))   # informamos a ejecutivo.py que si hay registro

    # Si está en la base de datos sacamos su nombre, lo dejamos disponible y lo dejamos escuchando
    name = db_ejecutivos[rut]["nombre"]
    print(f"[SERVER] Ejecutivo {name} conectado.")

    db_ejecutivos[rut]["disponible"] = 1
    actualizar_json(EJECUTIVOS_PATH, db_ejecutivos)
    # En el db de ejecutivos dejamos disponible al ejecutivo y comenzamos su loop en operations
    operations.start_ejecutivo(conn, name, rut)
    # Al terminar el loop lo dejamos como no disponible y cerramos la conexión
    print(f"[SERVER] Ejecutivo {name} desconectado.")
    db_ejecutivos[rut]["disponible"] = 0
    actualizar_json(EJECUTIVOS_PATH, db_ejecutivos)
    conn.close()


# Comienza el servidor, esperando conexiones y pasandoselas a handle_client en un cliente nuevo
def start_server():
    print(f"[ESCUCHANDO] Server está escuchando en {HOST}")
    server.listen()  # escuchamos a una nueva conexion
    while True:
        conn, addr = server.accept()  # esperamos nueva conexion al server
        # addr -> ip y puerto del que vino la conexion 
        # conn -> objeto que permite enviar info

        # Creamos thread para la nueva conexion que corre la fn handle_client con los argumentos args
        connection = read(conn) # Se recibe el tipo de conexión y se crea el thread correspondiente
        if connection == "cliente":
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()

        elif connection == "ejecutivo":
            thread = threading.Thread(target=handle_ejecutivo, args=(conn, addr))
            thread.start()

        else:
            print("Tipo de conexión desconocida")

        print(f"[SERVER] Conecciones activas {threading.active_count() - 1}")


print("[STARTING] server is starting...")
start_server()

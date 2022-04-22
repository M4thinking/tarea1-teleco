import socket
import threading
from db import *
from operations import *
import time

db = abrir_json("db.json")

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


# Corre en paralelo para cada cliente
def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    # Recibimos el rut con su primer mensaje del tamaño
    rut_len = conn.recv(HEADER).decode(FORMAT)
    if rut_len:
        rut_len = int(rut_len)
        rut = conn.recv(rut_len).decode(FORMAT)

    # Si no esta en la base de datos le pedimos el nombre
    if rut not in db:
        conn.send("0".encode(FORMAT)) # Indicamos que no tiene nombre y lo recibimos
        name_len = conn.recv(HEADER).decode(FORMAT)
        if name_len:
            name_len = int(name_len)
            name = conn.recv(name_len).decode(FORMAT)

            crear_cliente(db, rut, name)
            actualizar_json("preha.json", db)

    # Si ya esta en la base de datos sacamos su nombre y lo mandamos al cliente para que lo salude
    else:
        conn.send("1".encode(FORMAT)) # Indicamos al cliente que tenemos su nombre
        name = db[rut]["nombre"]

    print(f"[SERVER] Cliente {name} conectado.")

    conn.send(process_input(name).encode(FORMAT))

    connected = True
    while connected:
        conn.send(process_input(name).encode(FORMAT))
        # Manjemos tamaño del mensaje que viene
        data_len = conn.recv(HEADER).decode(FORMAT)# Espera hasta recibir data del cliente de tamaño bytes
        if data_len: # revisa si data_len no es NONE
            data_len = int(data_len)

            # Recivimos el mensaje completo
            data = conn.recv(data_len).decode(FORMAT)
            # Si envia el mensaje de desconexion terminamos el loop y cerramos la conexion
            if data == DISCONNECT_MESSAGE:
                connected = False

            print(f"[{addr}] {data}")

            conn.send("wena loco".encode(FORMAT))
    # Cerramos la conexion
    print(f"[SERVER] Cliente {name} desconectado.")
    conn.close()


# Comienza el servidor, esperando conexiones y pasandoselas a handle_client en un cliente nuevo
def start():
    print(f"[LISTENING] Server is listening on {HOST}")
    server.listen() # escuchamos a una nueva conexion
    while True:
        conn, addr = server.accept() # esperamos nueva conexion al server
        # addr -> ip y puerto del que vino la conexion 
        # conn -> objeto que permite enviar info
        # Creamos thread para la nueva conexion que corre la fn handle_client con los argumentos args
        thread = threading.Thread(target=handle_client, args = (conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() -1}")

print("[STARTING] server is starting...")
start()

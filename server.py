import socket
import threading
from db import *
from send_read import read
import operations

db = abrir_json("temp_db.json")

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
    conection = read(conn)
    rut = read(conn)     # Recibimos el rut

    # Si no esta en la base de datos le pedimos el nombre
    if rut not in db:
        conn.send("0".encode(FORMAT))  # Indicamos que no tiene nombre y lo recibimos
        name = read(conn)

        crear_cliente(db, rut, name)
        actualizar_json("temp_db.json", db)

    # Si ya esta en la base de datos sacamos su nombre y lo mandamos al cliente para que lo salude
    else:
        conn.send("1".encode(FORMAT))  # Indicamos al cliente que tenemos su nombre
        name = db[rut]["nombre"]

    print(f"[SERVER] Cliente {name} conectado.")

    # Comenzamos llamada desde operations
    operations.start_operations(conn, name, rut)

    # Cerramos la conexion
    conn.close()


def handle_ejecutivo(conn, adr):
    return


# Comienza el servidor, esperando conexiones y pasandoselas a handle_client en un cliente nuevo
def start():
    print(f"[LISTENING] Server is listening on {HOST}")
    server.listen()  # escuchamos a una nueva conexion
    while True:
        conn, addr = server.accept()  # esperamos nueva conexion al server
        # addr -> ip y puerto del que vino la conexion 
        # conn -> objeto que permite enviar info

        # Creamos thread para la nueva conexion que corre la fn handle_client con los argumentos args
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


print("[STARTING] server is starting...")
start()

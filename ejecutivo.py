import socket
from send_read import send, read

HEADER = 64
PORT = 6969
HOST = "127.0.0.1"
ADDR = (HOST, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

ejecutivo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ejecutivo.connect(ADDR)  # Nos conectamos al servidor!


def start():
    print(f"[NUEVA CONEXIÓN] Connected to {ADDR}")
    send(ejecutivo, "ejecutivo")
    print("[ASISTENTE] Hola! Bienvenido al portal de ejecutivos, Ingrese su RUT.")
    rut = input("[YO]: ")

    parse_rut = ''.join(char for char in rut if (char.isdigit() or char.upper() == 'K'))

    send(ejecutivo, parse_rut)
    # Recibimos de vuelta si el rut existe en la base de datos
    is_ejecutivo = read(ejecutivo)

    # Si no existe en el registro de ejecutivos terminamos el programa
    if is_ejecutivo == '1':
        print("[ASISTENTE] No estás registrado como ejecutivo!")
        return

    if is_ejecutivo == '2':
        print("[ASISTENTE] Ya hay una sesión abierta con tu rut!")
        return

    # Entramos a un loop infinito que recibe mensaje del servidor, lo mostramos en pantalla y le pedimos una
    # respuesta al ejecutivo, enviandola al servidor
    while True:
        server_msg = read(ejecutivo)

        if server_msg[0] != ':':
            print(f"{server_msg}")
            client_msg = input("[YO]: ")
            send(ejecutivo, client_msg)

        else:
            server_msg = server_msg[1:]
            if server_msg == DISCONNECT_MESSAGE:
                print("[ASISTENTE] Gracias por conectarse que tenga un buen día!")
                break
            else:
                print(f"{server_msg}")


start()
input("Presiones cualquier tecla para terminar")

import socket
from send_read import send

HEADER = 64
PORT = 6969
HOST = "192.168.56.1"
ADDR = (HOST, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)  # Nos conectamos al servidor!


def start():
    print(f"[NEW CONNECTION] Connected to {ADDR}")
    send(client, "cliente")
    print("[ASISTENTE] Hola! Bienvenido, Ingrese su RUT (con punto y guión.)")
    rut = input("[YO]: ")

    parse_rut = ''.join(char for char in rut if (char.isdigit() or char.upper() == 'K'))

    send(client, parse_rut)
    # Recibimos de vuelta si el rut existe en la base de datos
    has_name = client.recv(2048).decode(FORMAT)

    # Si no existe le pedimos el nombre y lo mandamos de vuelta
    # Si existe no necesitamos pedir el nombre para nada
    if has_name == '0':
        print("[ASISTENTE] Parece que eres nuevo por aca! Ingrese su nombre")
        name = input("[YO]: ")
        send(client, name)

    # Entramos a un loop infinito que recibe mensaje del servidor, lo mostramos en pantalla y le pedimos una
    # respuesta al cliente, enviandola al servidor
    while True:
        server_msg = client.recv(2048).decode(FORMAT)

        if server_msg[0] != ':':
            print(f"{server_msg}")
            client_msg = input("[YO]: ")
            send(client, client_msg)

        else:
            server_msg = server_msg[1:]
            if server_msg == DISCONNECT_MESSAGE:
                print("[ASISTENTE] Gracias por contactarnos que tenga un buen día!")
                break
            else:
                print(f"{server_msg}")


start()

import socket

HEADER = 64
PORT = 6969
HOST = "127.0.0.1"
ADDR = (HOST, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR) # Nos conectamos al servidor!


def send(msg):
    data = msg.encode(FORMAT)   # Codificamos siguiendo el mismo formato
    data_len = len(data)
    send_len = str(data_len).encode(FORMAT)
    
    # Enviamos send_len (extendido a 68B) y luego enviamos el mensaje
    send_len += b' ' * (HEADER - len(send_len))
    client.send(send_len)
    client.send(data)


def start():
    print(f"[NEW CONNECTION] Connected to {ADDR}")
    print("[ASISTENTE] Hola! Bienvenido, Ingrese su RUT (con punto y guión.)")
    rut = input("[YO]: ")
    
    parse_rut = ''.join(char for char in rut if (char.isdigit() or char.upper() == 'K'))
    
    # print(parse_rut)
    
    send(parse_rut)
    # Recibimos de vuelta si el rut existe en la base de datos
    has_name = client.recv(2048).decode(FORMAT)
    
    # Si no existe le pedimos el nombre y lo mandamos de vuelta
    if has_name == '0':
        print("[ASISTENTE] Parece que eres nuevo por aca! Ingrese su nombre")
        name = input("[YO]: ")
        send(name)
    
    # Si existe recibimos el nombre del server
    else:
        pass
        #name = client.recv(2048).decode(FORMAT)
    
    print(f"[ASISTENTE] Para desconectarse enviar '{DISCONNECT_MESSAGE}'.")
    
    # Entramos a un loop infinito que recibe mensaje del servidor, lo mostramos en pantalla y le pedimos una respuesta al cliente, enviandola al servidor
    connected = True
    while connected:
        server_msg = client.recv(2048).decode(FORMAT)
        print(f"[ASISTENTE] {server_msg}")
        
        client_msg = input("[YO]: ")
        if client_msg == DISCONNECT_MESSAGE:  
                connected = False
        
        send(client_msg)

start()

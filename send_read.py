HEADER = 64
FORMAT = 'utf-8'


# Envia mensajes usando nuestro estandar de header (largo de mensaje) + mensaje
def send(socket, msg):
    data = msg.encode(FORMAT)  # Codificamos siguiendo el mismo formato
    data_len = len(data)
    send_len = str(data_len).encode(FORMAT)

    # Enviamos send_len (extendido a 68 Bytes) y luego enviamos el mensaje
    send_len += b' ' * (HEADER - len(send_len))
    socket.send(send_len)
    socket.send(data)


# Lee mensaje usando nuestro estandar de header + mensaje
def read(conn):
    msg_len = conn.recv(HEADER).decode(FORMAT)
    if msg_len:
        msg_len = int(msg_len)
        msg = conn.recv(msg_len).decode(FORMAT)
        return msg


import db


def check_attentions(name, message):
    data = db.abrir_json("db.json")
    return 1


def reset_service(name, message):
    print(f"[SERVER] Reinicio Servicios Cliente {name}.")
    return 2


def contact_operator(name, message):
    print(f"[SERVER] Cliente {name} redirigido a ejecutivo {operator}.")
    return 3


def server_exit(name, message):
    print(f"[SERVER] Cliente {name} desconectado.")
    return 4


# Esta no nos sirve mucho
def process_input(data):
    try:
        op = int(data)
        if 0 < op < 4:
            name = "Jorge"
            options = {
                "1": {"Revisar atenciones anteriores": {
                    "Usted tiene las siguientes solicitudes en curso:": check_attentions
                }
                },
                "2": {"Reiniciar servicios": {
                    "Reseteando el servicio...": reset_service
                }
                },
                "3": {"Contactar a un ejecutivo": {
                    "Estamos redirigiendo a un asistente, usted está numero 3 en la fila": contact_operator
                }
                },
                "4": {"Salir": {
                    "Gracias por contactarnos que tenga un buen día.": server_exit
                }
                }
            }
            print("Processing the input received from client")

            message = f"""  Hola {name}, en qué te podemos ayudar?.\n\n"""
            for key, value in options.items():
                for subkey in value.items():
                    message += f"""\t({key}) {subkey[0]}.\n"""
            return message
    except:
        return "Ingresa una entrada válida."
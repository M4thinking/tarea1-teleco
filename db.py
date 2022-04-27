import json
import threading

mutex = threading.Lock()  # Creamos un objeto mutex


# Abrimos un .JSON para trabajar
def abrir_json(nombreArchivo):
    global mutex  # Traemos el objeto mutex
    mutex.acquire()  # Pedimos permiso para que solo el hilo actual pueda realizar el proceso
    f = open(nombreArchivo)  # Abrimos el archivo
    data = json.load(f)  # Guardamos el .json en un diccionario
    f.close()  # Cerramos el archvo
    mutex.release()  # Soltamos el mutex de este hilo
    return data  # Retornamos el diccionario


# Actualiamos el .JSON ya trabajado
def actualizar_json(nombreArchivo, data):
    global mutex  # Traemos el objeto mutex
    mutex.acquire()  # Pedimos permiso para que solo el hilo actual pueda realizar el proceso
    f = open(nombreArchivo, "w")  # Abrimos el archivo
    json.dump(data, f, indent=4)  # Reescribimos el .json
    f.close()  # Cerramos el archvo
    mutex.release()  # Soltamos el mutex de este hilo
    return True  # Retornamos un booleano que verifica que se completo el proceso


# Creamos un nuevo cliente en el diccionario con el que trabajamos
def crear_cliente(Dict, Rut, nombre):
    # Revisamos si el rut ya existe entre las llaves
    if not Rut in Dict:
        Var = {
            "nombre": "",
            "atenciones": {}
        }
        Var["nombre"] = nombre  # Creamos la llave con los datos del cliente
        Dict.update({Rut: Var})  # Actualizamos el diccionario
        return True  # Retornamos un booleno que verifica que se realizó el proceso
    else:
        return False


# Creamos una nueva atencion
def crear_atencion(Dict, Rut, ID, descripcion):
    Att = {
        "estado": True,
        "descripcion": descripcion,
        "historial": {}
    }
    # Revisamos si ya hay una atención con ese ID
    if not ID in Dict[Rut]["atenciones"]:
        Dict[Rut]["atenciones"][ID] = Att  # actualizamos el diccionario con la nueva atencion
        return True  # Retornamos un boolenao que verifica que se realizó el proceso
    else:
        return False


# Creamos un historial
def crear_historial(Dict, ID, fecha, contenido):
    # Revisamos si ya hay un historial con esa fecha
    if not fecha in Dict["atenciones"][ID]["historial"]:
        # Insertamos un elemento en el diccionario de historiales
        Dict["atenciones"][ID]["historial"][fecha] = contenido
        return True  # Retornamos un boolenao que verifica que se realizó el proceso
    else:
        return False


# Creamos una funcion que reinicia los servicios
def reiniciar_servicios(Dict):
    Dict["atenciones"] = {}  # Actualizamos la llave que contiene las atenciones para que sea un dccionario vacio
    return True  # Retornamos un boolenao que verifica que se realizó el proceso

import json
import threading

mutex = threading.Lock()  # Creamos un objeto mutex


# Abrimos un .JSON para trabajar
def abrir_json(nombre_archivo):
    global mutex  # Traemos el objeto mutex
    mutex.acquire()  # Pedimos permiso para que solo el hilo actual pueda realizar el proceso
    f = open(nombre_archivo)  # Abrimos el archivo
    data = json.load(f)  # Guardamos el .json en un diccionario
    f.close()  # Cerramos el archvo
    mutex.release()  # Soltamos el mutex de este hilo
    return data  # Retornamos el diccionario


# Actualiamos el .JSON ya trabajado
def actualizar_json(nombre_archivo, data):
    global mutex  # Traemos el objeto mutex
    mutex.acquire()  # Pedimos permiso para que solo el hilo actual pueda realizar el proceso
    f = open(nombre_archivo, "w")  # Abrimos el archivo
    json.dump(data, f, indent=4)  # Reescribimos el .json
    f.close()  # Cerramos el archvo
    mutex.release()  # Soltamos el mutex de este hilo
    return True  # Retornamos un booleano que verifica que se completo el proceso


# Creamos un nuevo cliente en el diccionario con el que trabajamos
def crear_cliente(db, rut, nombre):
    # Revisamos si el rut ya existe entre las llaves
    if not rut in db:
        Var = {
            "nombre": "",
            "atenciones": {}
        }
        Var["nombre"] = nombre  # Creamos la llave con los datos del cliente
        db.update({rut: Var})  # Actualizamos el diccionario
        return True  # Retornamos un booleno que verifica que se realizó el proceso
    else:
        return False


# Creamos una nueva atencion
def crear_atencion(db, rut, id, descripcion):
    Att = {
        "estado": True,
        "descripcion": descripcion,
        "historial": {}
    }
    # Revisamos si ya hay una atención con ese ID
    if not id in db[rut]["atenciones"]:
        db[rut]["atenciones"][id] = Att  # actualizamos el diccionario con la nueva atencion
        return True  # Retornamos un boolenao que verifica que se realizó el proceso
    else:
        return False


# Creamos un historial
def crear_historial(db, id, fecha, contenido):
    # Revisamos si ya hay un historial con esa fecha
    if not fecha in db["atenciones"][id]["historial"]:
        # Insertamos un elemento en el diccionario de historiales
        db["atenciones"][id]["historial"][fecha] = contenido
        return True  # Retornamos un boolenao que verifica que se realizó el proceso
    else:
        return False


# # Creamos una funcion que reinicia los servicios (mal entendimiento del enunciado)
# def reiniciar_servicios(db):
#     db["atenciones"] = {}  # Actualizamos la llave que contiene las atenciones para que sea un diccionario vacío
#     return True  # Retornamos un boolenao que verifica que se realizó el proceso

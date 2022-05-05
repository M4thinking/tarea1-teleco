import json
import threading

mutex = threading.Lock()  # Creamos un objeto mutex


# Abrimos un ".JSON" para trabajar
def abrir_json(nombre_archivo):
    global mutex  # Traemos el objeto mutex
    mutex.acquire()  # Pedimos permiso para que solo el hilo actual pueda realizar el proceso
    f = open(nombre_archivo, encoding='utf-8')  # Abrimos el archivo
    data = json.load(f)  # Guardamos él ".JSON" en un diccionario
    f.close()  # Cerramos el archivo
    mutex.release()  # Soltamos el mutex de este hilo
    return data  # Retornamos el diccionario


# Actualizamos el ".JSON" ya trabajado
def actualizar_json(nombre_archivo, data):
    global mutex  # Traemos el objeto mutex
    mutex.acquire()  # Pedimos permiso para que solo el hilo actual pueda realizar el proceso
    f = open(nombre_archivo, "w", encoding='utf-8')  # Abrimos el archivo
    json.dump(data, f, indent=4, ensure_ascii=False)  # Reescribimos el .json
    f.close()  # Cerramos el archivo
    mutex.release()  # Soltamos el mutex de este hilo
    return True  # Retornamos un booleano que verifica que se completo el proceso


# Creamos un nuevo cliente en el diccionario con el que trabajamos
def crear_cliente(db, rut, nombre):
    # Revisamos si el rut ya existe entre las llaves
    if rut not in db:
        Var = {"nombre": nombre, "atenciones": {}}
        db.update({rut: Var})  # Actualizamos el diccionario
        return True  # Retornamos un booleno que verifica que se realizó el proceso
    else:
        return False


# Creamos una nueva atencion
def crear_atencion(db, rut, id_att, descripcion):
    Att = {
        "estado": True,
        "descripcion": descripcion,
        "historial": {}
    }
    # Revisamos si ya hay una atención con ese ID
    if id_att not in db[rut]["atenciones"]:
        db[rut]["atenciones"][id_att] = Att  # actualizamos el diccionario con la nueva atencion
        return True  # Retornamos un boolenao que verifica que se realizó el proceso
    else:
        return False


# Modificamos la descripción de la atención
def modificar_descripcion(db, rut, id_att, descripcion):
    db[rut]["atenciones"][id_att]["descripcion"] = descripcion  # actualizamos el diccionario con la nueva descripcion
    return


# Modificamos el estado de la atención
def modificar_estado(db, rut, id_att, estado):
    db[rut]["atenciones"][id_att]["estado"] = estado  # actualizamos el diccionario con la nueva descripcion
    return


# Creamos un historial
def crear_historial(db, rut, id_att, fecha, contenido):
    # Insertamos un elemento en el diccionario de historiales
    db[rut]["atenciones"][id_att]["historial"][fecha] = contenido
    return

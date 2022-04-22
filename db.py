import json

Usuario_defecto = {
                    "nombre": "",
                    "atenciones": {}
                  }
Atencion_defecto = {
 "estado":True,
  "descripcion":"",
  "historial":{} 
}


# Abrimos un .JSON para trabajar
def abrir_json(nombreArchivo):
  f = open(nombreArchivo)
  data = json.dumps(f)
  return data

# Actualiamos el .JSON ya trabajado
def actualizar_json(nombreArchivo, data):
  f = open(nombreArchivo, "w")
  json.dump(data, f)
  f.close()
  return True


# Creamos un nuevo cliente en el diccionario con el que trabajamos
def crear_cliente(Dict, Rut, nombre):
  # Revisamos si el rut ya existe entre las llaves
  if not Rut in Dict:
    Var = {
                    "nombre": "",
                    "atenciones": {}
                  }
    Var["nombre"] = nombre
    Dict.update({Rut:Var})
    return True
  else:
    return False

# Creamos una nueva atencion
def crear_atencion(Dict, ID, descripcion):
  Att = {
  "estado":True,
  "descripcion":descripcion,
  "historial":{} }

  # Revisamos si ya hay una atención con ese ID
  if not ID in Dict:
    Dict["atenciones"][ID] = Att
    return True
  else:
    return False

# Creamos un historial
def crear_historial(Dict,ID, fecha, contenido):
  if not fecha in Dict["atenciones"][ID]["historial"]:
    Dict["atenciones"][ID]["historial"][fecha] = contenido
    return True
  else: 
    return False

# Creamos una funcion que reinicia los servicios
def reiniciar_servicios(Dict):
  Dict["atenciones"] = {}
  return Dict

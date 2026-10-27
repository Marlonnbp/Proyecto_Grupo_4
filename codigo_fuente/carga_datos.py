import csv
import os

from codigo_fuente.nodo import NodoSensor

def cargar_datos_csv(ruta_csv, grafo, tabla_hash=None):
    #Carga los sensores del CSV al grafo y devuelve la cantidad cargada.
    if not os.path.exists(ruta_csv):
        raise FileNotFoundError(f"No se encontró el archivo de datos en: {ruta_csv}")

    sensores_cargados = 0
    ids_vistos = set()

    with open(ruta_csv, mode='r', encoding='utf-8-sig', newline='') as archivo:
        lector = csv.DictReader(archivo, delimiter=';')

        for numero_fila, fila in enumerate(lector, start=2):
            if not any(valor and valor.strip() for valor in fila.values()):
                continue

            try:
                id_sensor = fila['ID_Sensor'].strip()
                ciudad = fila['Ciudad'].strip()
                latitud = float(fila['Latitud'].strip())
                longitud = float(fila['Longitud'].strip())
                altitud = float(fila['Altitud'].strip())
                interferencia = int(fila['Interferencia_RF'].strip())
                tipo_suelo = int(fila['Tipo_Suelo'].strip())
            except (KeyError, ValueError, AttributeError) as error:
                raise ValueError(f"Fila {numero_fila} inválida en {ruta_csv}: {error}")

            if id_sensor in ids_vistos:
                raise ValueError(f"Fila {numero_fila}: ID_Sensor repetido ({id_sensor})")
            if not 1 <= interferencia <= 10:
                raise ValueError(f"Fila {numero_fila}: Interferencia_RF fuera de 1 a 10")
            if tipo_suelo not in (1, 2, 3):
                raise ValueError(f"Fila {numero_fila}: Tipo_Suelo debe ser 1, 2 o 3")

            sensor = NodoSensor(
                id_sensor=id_sensor,
                ciudad=ciudad,
                latitud=latitud,
                longitud=longitud,
                altitud=altitud,
                interferencia_rf=interferencia,
                tipo_suelo=tipo_suelo,
            )

            grafo.agregar_vertice(sensor)
            if tabla_hash is not None:
                tabla_hash.insertar(sensor.id, sensor)

            ids_vistos.add(id_sensor)
            sensores_cargados += 1

    return sensores_cargados
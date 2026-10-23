import csv
import os
from nodo import NodoSensor

def cargar_datos_csv(ruta_csv, grafo, tabla_hash=None):
    
    if not os.path.exists(ruta_csv):
        raise FileNotFoundError(f"No se encontró el archivo de datos en: {ruta_csv}")

    sensores_cargados = 0

    with open(ruta_csv, mode='r', encoding='utf-8') as archivo:
        # Se utiliza DictReader estándar de Python
        lector = csv.DictReader(archivo)
        
        for fila in lector:
            # Extracción y limpieza de cada campo según la regla RN-01
            id_sensor = fila['ID_Sensor'].strip()
            ciudad = fila['Ciudad'].strip()
            latitud = float(fila['Latitud'].strip())
            longitud = float(fila['Longitud'].strip())
            altitud = float(fila['Altitud'].strip())
            interferencia = int(fila['Interferencia_RF'].strip())
            tipo_suelo = int(fila['Tipo_Suelo'].strip())

            # Creación de la instancia en memoria dinámica
            sensor = NodoSensor(
                id_sensor=id_sensor,
                ciudad=ciudad,
                latitud=latitud,
                longitud=longitud,
                altitud=altitud,
                interferencia_rf=interferencia,
                tipo_suelo=tipo_suelo
            )

            # Se agrega como vértice al Grafo base
            grafo.agregar_vertice(sensor)

            sensores_cargados += 1

    return sensores_cargados
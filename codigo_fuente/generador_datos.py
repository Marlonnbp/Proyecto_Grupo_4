import csv
import math
import random


SEMILLA = 42
NUM_EJEMPLOS = 5000
RUTA_DEFECTO = "datos/entrenamiento_enlaces.csv"
ENCABEZADO = ["Distancia_km", "Dif_Altitud_m", "Interferencia_Prom", "Costo"]

# Rango geográfico aproximado del Perú (para generar distancias realistas)
LAT_MIN, LAT_MAX = -18.3, -0.1
LON_MIN, LON_MAX = -81.3, -68.7
ALT_MAX = 4800            # metros
RADIO_TIERRA_KM = 6371.0

# Parámetros del costo (RN-03: positivo, con un valor mínimo)
COSTO_MINIMO = 1.0
PESO_DISTANCIA = 1.0       # por km
PESO_ALTITUD = 0.05        # por metro de diferencia de altitud
PESO_INTERFERENCIA = 10.0  # por punto de interferencia (escala 1 a 10)
PESO_CRUCE = 0.02          # interacción distancia x interferencia (parte no lineal)
RUIDO_RELATIVO = 0.03      # ruido gaussiano de 3 % sobre el costo


def haversine(lat1, lon1, lat2, lon2):
    """Distancia en km entre dos puntos de la Tierra (fórmula de Haversine)."""
    f1, f2 = math.radians(lat1), math.radians(lat2)
    df = f2 - f1
    dl = math.radians(lon2 - lon1)
    a = math.sin(df / 2) ** 2 + math.cos(f1) * math.cos(f2) * math.sin(dl / 2) ** 2
    return 2 * RADIO_TIERRA_KM * math.asin(math.sqrt(min(1.0, a)))


def costo_enlace(distancia_km, dif_altitud_m, interferencia_prom):
    """Costo sin ruido: parte lineal más un término de cruce distancia x interferencia."""
    lineal = (COSTO_MINIMO
              + PESO_DISTANCIA * distancia_km
              + PESO_ALTITUD * dif_altitud_m
              + PESO_INTERFERENCIA * interferencia_prom)
    return lineal + PESO_CRUCE * distancia_km * interferencia_prom


def _limitar(valor, minimo, maximo):
    return max(minimo, min(maximo, valor))


def generar_dataset(n=NUM_EJEMPLOS, semilla=SEMILLA):
    """Devuelve una lista de n filas [distancia, dif_altitud, interferencia_prom, costo]."""
    rng = random.Random(semilla)  # generador propio con semilla fija (equivale a random.seed(42))
    filas = []
    for _ in range(n):
        lat1 = rng.uniform(LAT_MIN, LAT_MAX)
        lon1 = rng.uniform(LON_MIN, LON_MAX)
        if rng.random() < 0.3:
            # Parte de los enlaces son cercanos, como entre ciudades vecinas
            lat2 = _limitar(lat1 + rng.uniform(-2.5, 2.5), LAT_MIN, LAT_MAX)
            lon2 = _limitar(lon1 + rng.uniform(-2.5, 2.5), LON_MIN, LON_MAX)
        else:
            lat2 = rng.uniform(LAT_MIN, LAT_MAX)
            lon2 = rng.uniform(LON_MIN, LON_MAX)

        distancia = haversine(lat1, lon1, lat2, lon2)

        alt1 = rng.triangular(0, ALT_MAX, 800)   # la mayoría de sensores está a baja altitud
        alt2 = rng.triangular(0, ALT_MAX, 800)
        dif_altitud = abs(alt1 - alt2)

        interferencia = (rng.randint(1, 10) + rng.randint(1, 10)) / 2

        costo = costo_enlace(distancia, dif_altitud, interferencia)
        costo *= 1 + rng.gauss(0, RUIDO_RELATIVO)
        costo = max(COSTO_MINIMO, costo)

        filas.append([round(distancia, 4), round(dif_altitud, 4),
                      round(interferencia, 2), round(costo, 4)])
    return filas


def guardar_csv(filas, ruta=RUTA_DEFECTO):
    """Guarda el dataset en CSV. La carpeta de destino debe existir."""
    with open(ruta, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(ENCABEZADO)
        escritor.writerows(filas)


def cargar_csv(ruta=RUTA_DEFECTO):
    """Lee el CSV y devuelve (entradas, salidas) listos para el MLP."""
    entradas, salidas = [], []
    with open(ruta, newline="", encoding="utf-8") as archivo:
        lector = csv.reader(archivo)
        next(lector)  # encabezado
        for fila in lector:
            entradas.append([float(fila[0]), float(fila[1]), float(fila[2])])
            salidas.append(float(fila[3]))
    return entradas, salidas


if __name__ == "__main__":
    datos = generar_dataset()
    guardar_csv(datos)
    costos = [f[3] for f in datos]
    print(f"{len(datos)} ejemplos guardados en {RUTA_DEFECTO} (semilla {SEMILLA})")
    print(f"Costo mínimo: {min(costos):.2f} | máximo: {max(costos):.2f} | "
          f"promedio: {sum(costos) / len(costos):.2f}")
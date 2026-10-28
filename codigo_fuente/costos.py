import math

from codigo_fuente.lista_enlazada import ListaEnlazada
from codigo_fuente.nodo import NodoSensor

RADIO_TIERRA_KM = 6371.0

# Parámetros de la fórmula lineal (mismos valores que generador_datos.py)
COSTO_MINIMO = 1.0
PESO_DISTANCIA = 1.0        # por km
PESO_ALTITUD = 0.05         # por metro de diferencia de altitud
PESO_INTERFERENCIA = 10.0   # por punto de interferencia (escala 1 a 10)


def haversine(lat1, lon1, lat2, lon2):
    """Distancia en km entre dos puntos de la Tierra dados en grados."""
    f1, f2 = math.radians(lat1), math.radians(lat2)
    delta_f = f2 - f1
    delta_l = math.radians(lon2 - lon1)
    a = (math.sin(delta_f / 2) ** 2
         + math.cos(f1) * math.cos(f2) * math.sin(delta_l / 2) ** 2)
    return 2 * RADIO_TIERRA_KM * math.asin(math.sqrt(min(1.0, a)))


def distancia_sensores(a: NodoSensor, b: NodoSensor):
    return haversine(a.latitud, a.longitud, b.latitud, b.longitud)


def diferencia_altitud(a: NodoSensor, b: NodoSensor):
    return abs(a.altitud - b.altitud)


def interferencia_promedio(a: NodoSensor, b: NodoSensor):
    return (a.interferencia_rf + b.interferencia_rf) / 2


def costo_lineal(distancia_km, dif_altitud_m, interferencia_prom):
    """Fórmula lineal ponderada. Nunca devuelve menos que COSTO_MINIMO."""
    costo = (COSTO_MINIMO
             + PESO_DISTANCIA * distancia_km
             + PESO_ALTITUD * dif_altitud_m
             + PESO_INTERFERENCIA * interferencia_prom)
    return max(COSTO_MINIMO, costo)


def _ordenar_par(a: NodoSensor, b: NodoSensor):
    """Ordena el par por ID para que A-B y B-A se calculen exactamente igual."""
    return (a, b) if a.id <= b.id else (b, a)


def calcular_costo(a: NodoSensor, b: NodoSensor, predictor=None):
    """Costo del enlace entre dos sensores.

    predictor: función opcional (distancia_km, dif_altitud_m, interferencia_prom)
    que devuelve el costo estimado por el MLP. Si no se entrega, si lanza un
    error o si devuelve un valor no válido (NaN, infinito o <= 0), se usa la
    fórmula lineal como respaldo.
    """
    a, b = _ordenar_par(a, b)
    distancia = distancia_sensores(a, b)
    dif_altitud = diferencia_altitud(a, b)
    interferencia = interferencia_promedio(a, b)

    if predictor is not None:
        try:
            costo = float(predictor(distancia, dif_altitud, interferencia))
            if math.isfinite(costo) and costo > 0:
                return max(COSTO_MINIMO, costo)
        except Exception:
            pass  # el MLP falló: se usa la fórmula lineal

    return costo_lineal(distancia, dif_altitud, interferencia)


def cantidad_enlaces(n_sensores):
    """Número de enlaces candidatos no dirigidos: n x (n - 1) / 2."""
    return n_sensores * (n_sensores - 1) // 2


def calcular_costos_enlaces(sensores: ListaEnlazada, predictor=None):
    """Calcula el costo de todos los pares de sensores.

    Recibe una ListaEnlazada de NodoSensor (por ejemplo grafo.vertices) y
    devuelve una ListaEnlazada de tuplas (id_u, id_v, costo) con id_u < id_v,
    una por cada enlace candidato (351 para 27 sensores).
    """
    if not isinstance(sensores, ListaEnlazada):
        raise TypeError("sensores debe ser una ListaEnlazada de NodoSensor")

    enlaces = ListaEnlazada()
    nodo_i = sensores.cabeza
    while nodo_i is not None:
        nodo_j = nodo_i.siguiente
        while nodo_j is not None:
            a, b = _ordenar_par(nodo_i.dato, nodo_j.dato)
            enlaces.agregar_al_final((a.id, b.id, calcular_costo(a, b, predictor)))
            nodo_j = nodo_j.siguiente
        nodo_i = nodo_i.siguiente
    return enlaces
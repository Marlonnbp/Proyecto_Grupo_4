from codigo_fuente.cola_prioridad import ColaPrioridad
from codigo_fuente.tabla_hash import TablaHash
from codigo_fuente.simulacion_alerta import reconstruir_ruta

# Nombres posibles de los atributos de Arista (ajustar si hace falta).
_NOMBRES_DESTINO = ("destino", "id_destino", "v", "hasta")
_NOMBRES_COSTO = ("costo", "peso")


def _leer(arista, nombres):
    for nombre in nombres:
        if hasattr(arista, nombre):
            return getattr(arista, nombre)
    raise AttributeError(
        f"Arista no tiene ninguno de estos atributos: {nombres}. "
        "Ajusta _NOMBRES_DESTINO / _NOMBRES_COSTO en dijkstra.py"
    )


def dijkstra(grafo, id_origen, id_destino=None):
    if id_origen not in grafo.adyacencias:
        raise KeyError(f"Sensor inexistente: {id_origen}")

    distancias = TablaHash()
    predecesores = TablaHash()
    visitados = TablaHash()

    distancias.insertar(id_origen, 0)
    predecesores.insertar(id_origen, None)

    cola = ColaPrioridad()
    cola.insertar((0, id_origen))  # el empate se rompe por ID: resultado estable

    while not cola.esta_vacia():
        costo_actual, actual = cola.extraer_minimo()

        if visitados.contiene(actual):
            continue  # entrada vieja: ya se encontró un camino mejor
        visitados.insertar(actual, True)

        if actual == id_destino:
            break

        for arista in grafo.obtener_vecinos(actual):
            vecino = _leer(arista, _NOMBRES_DESTINO)
            costo = _leer(arista, _NOMBRES_COSTO)

            if costo <= 0:
                raise ValueError(
                    f"Dijkstra exige costos positivos (enlace {actual}-{vecino}: {costo})"
                )
            if visitados.contiene(vecino):
                continue

            nuevo = costo_actual + costo
            previo = distancias.buscar(vecino)
            if previo is None or nuevo < previo:
                distancias.insertar(vecino, nuevo)
                predecesores.insertar(vecino, actual)
                cola.insertar((nuevo, vecino))

    return distancias, predecesores


def ruta_optima(grafo, id_origen, id_destino):
    distancias, predecesores = dijkstra(grafo, id_origen, id_destino)
    if not distancias.contiene(id_destino):
        return None
    ruta = reconstruir_ruta(predecesores, id_origen, id_destino)
    if ruta is None:
        return None
    return ruta, distancias.buscar(id_destino)


def crear_calcular_ruta(grafo_operativo):
    def calcular_ruta(id_origen, id_destino):
        return ruta_optima(grafo_operativo, id_origen, id_destino)
    return calcular_ruta




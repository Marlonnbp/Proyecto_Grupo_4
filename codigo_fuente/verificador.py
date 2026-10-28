from codigo_fuente.lista_enlazada import ListaEnlazada


def _construir_adyacencia(ids, aristas):
    adyacencia = {id_sensor: ListaEnlazada() for id_sensor in ids}
    for arista in aristas:
        adyacencia[arista.origen].agregar_al_final(arista.destino)
        adyacencia[arista.destino].agregar_al_final(arista.origen)
    return adyacencia


def _dfs(adyacencia, actual, padre, visitados):
    visitados.add(actual)
    hay_ciclo = False
    for vecino in adyacencia[actual]:
        if vecino not in visitados:
            if _dfs(adyacencia, vecino, actual, visitados):
                hay_ciclo = True
        elif vecino != padre:
            hay_ciclo = True
    return hay_ciclo


def es_conexo(ids, aristas):
    ids = list(ids)
    if not ids:
        return True
    adyacencia = _construir_adyacencia(ids, aristas)
    visitados = set()
    _dfs(adyacencia, ids[0], None, visitados)
    return len(visitados) == len(ids)


def tiene_ciclos(ids, aristas):
    ids = list(ids)
    adyacencia = _construir_adyacencia(ids, aristas)
    visitados = set()
    for id_sensor in ids:
        if id_sensor not in visitados:
            if _dfs(adyacencia, id_sensor, None, visitados):
                return True
    return False


def verificar_arbol(grafo, arbol):
    ids = [sensor.id for sensor in grafo.vertices]
    aristas = list(arbol)
    esperadas = len(ids) - 1
    conexo = es_conexo(ids, aristas)
    sin_ciclos = not tiene_ciclos(ids, aristas)
    return {
        'aristas_esperadas': esperadas,
        'aristas_obtenidas': len(aristas),
        'conexo': conexo,
        'sin_ciclos': sin_ciclos,
        'costo_total': sum(arista.costo for arista in aristas),
        'valido': len(aristas) == esperadas and conexo and sin_ciclos,
    }


def verificar_red_operativa(grafo, aristas):
    ids = [sensor.id for sensor in grafo.vertices]
    aristas = list(aristas)
    return {
        'aristas': len(aristas),
        'conexa': es_conexo(ids, aristas),
        'costo_total': sum(arista.costo for arista in aristas),
    }
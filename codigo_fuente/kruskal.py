from codigo_fuente.cola_prioridad import ColaPrioridad
from codigo_fuente.lista_enlazada import ListaEnlazada
from codigo_fuente.union_find import UnionFind


def kruskal(grafo):

    cola = ColaPrioridad()
    for arista in grafo.aristas:
        cola.insertar(arista)

    conjuntos = UnionFind(sensor.id for sensor in grafo.vertices)
    arbol = ListaEnlazada()
    costo_total = 0.0
    objetivo = grafo.cantidad_vertices() - 1

    while not cola.esta_vacia() and arbol.obtener_tamano() < objetivo:
        arista = cola.extraer_minimo()
        if conjuntos.union(arista.origen, arista.destino):
            arbol.agregar_al_final(arista)
            costo_total += arista.costo

    return arbol, costo_total
import random
import time

from codigo_fuente.cola_prioridad import ColaPrioridad


class ColaPrioridadLista:
    def __init__(self):
        self._datos = []

    def esta_vacia(self):
        return len(self._datos) == 0

    def insertar(self, elemento):
        self._datos.append(elemento)

    def extraer_minimo(self):
        posicion_minimo = 0
        for i in range(1, len(self._datos)):
            if self._datos[i] < self._datos[posicion_minimo]:
                posicion_minimo = i
        self._datos[posicion_minimo], self._datos[-1] = self._datos[-1], self._datos[posicion_minimo]
        return self._datos.pop()


def medir(clase_cola, valores):
    cola = clase_cola()
    inicio = time.perf_counter()
    for valor in valores:
        cola.insertar(valor)
    extraidos = []
    while not cola.esta_vacia():
        extraidos.append(cola.extraer_minimo())
    return time.perf_counter() - inicio, extraidos


def comparar(tamanos=(1000, 2000, 4000, 8000), semilla=42):
    random.seed(semilla)
    print(f"{'N':>8} {'Heap (s)':>12} {'Lista (s)':>12} {'Lista/Heap':>12}")
    for n in tamanos:
        valores = [random.random() for _ in range(n)]
        tiempo_heap, orden_heap = medir(ColaPrioridad, valores)
        tiempo_lista, orden_lista = medir(ColaPrioridadLista, valores)
        assert orden_heap == orden_lista
        print(f"{n:>8} {tiempo_heap:>12.4f} {tiempo_lista:>12.4f} {tiempo_lista / tiempo_heap:>12.1f}")


if __name__ == '__main__':
    comparar()
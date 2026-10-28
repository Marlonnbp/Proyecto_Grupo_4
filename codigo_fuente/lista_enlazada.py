from codigo_fuente.nodo import NodoLista

class ListaEnlazada:
    """Lista simplemente enlazada dinámica implementada sin librerías externas."""
    def __init__(self):
        self.cabeza = None
        self._tamano = 0

    def esta_vacia(self):
        return self.cabeza is None

    def agregar_al_final(self, dato):
        nuevo = NodoLista(dato)
        if self.esta_vacia():
            self.cabeza = nuevo
        else:
            actual = self.cabeza
            while actual.siguiente is not None:
                actual = actual.siguiente
            actual.siguiente = nuevo
        self._tamano += 1

    def obtener_tamano(self):
        return self._tamano

    def __iter__(self):
        """Generador para poder recorrer la lista de forma iterativa."""
        actual = self.cabeza
        while actual is not None:
            yield actual.dato
            actual = actual.siguiente

    def __repr__(self):
        elementos = [str(x) for x in self]
        return " -> ".join(elementos) if elementos else "ListaVacia"
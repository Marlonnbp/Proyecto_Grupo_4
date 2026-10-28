
class _NodoPila:
    __slots__ = ("dato", "siguiente")

    def __init__(self, dato, siguiente=None):
        self.dato = dato
        self.siguiente = siguiente


class Pila:

    def __init__(self):
        self._tope = None
        self._tamano = 0

    def apilar(self, dato):
        self._tope = _NodoPila(dato, self._tope)
        self._tamano += 1

    def desapilar(self):
        if self._tope is None:
            raise IndexError("La pila está vacía")
        dato = self._tope.dato
        self._tope = self._tope.siguiente
        self._tamano -= 1
        return dato

    def ver_tope(self):
        if self._tope is None:
            raise IndexError("La pila está vacía")
        return self._tope.dato

    def esta_vacia(self):
        return self._tope is None

    def tamano(self):
        return self._tamano

    def __len__(self):
        return self._tamano

    def __iter__(self):
        actual = self._tope
        while actual is not None:
            yield actual.dato
            actual = actual.siguiente
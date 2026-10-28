class ColaPrioridad:
    """Heap binario mínimo. Los elementos deben ser comparables con <."""

    def __init__(self):
        self._datos = []

    def esta_vacia(self):
        return len(self._datos) == 0

    def obtener_tamano(self):
        return len(self._datos)

    def insertar(self, elemento):
        self._datos.append(elemento)
        self._subir(len(self._datos) - 1)

    def ver_minimo(self):
        if self.esta_vacia():
            raise IndexError("La cola de prioridad está vacía")
        return self._datos[0]

    def extraer_minimo(self):
        if self.esta_vacia():
            raise IndexError("La cola de prioridad está vacía")
        minimo = self._datos[0]
        ultimo = self._datos.pop()
        if self._datos:
            self._datos[0] = ultimo
            self._bajar(0)
        return minimo

    def _subir(self, i):
        while i > 0:
            padre = (i - 1) // 2
            if self._datos[i] < self._datos[padre]:
                self._datos[i], self._datos[padre] = self._datos[padre], self._datos[i]
                i = padre
            else:
                break

    def _bajar(self, i):
        n = len(self._datos)
        while True:
            izquierdo = 2 * i + 1
            derecho = izquierdo + 1
            menor = i
            if izquierdo < n and self._datos[izquierdo] < self._datos[menor]:
                menor = izquierdo
            if derecho < n and self._datos[derecho] < self._datos[menor]:
                menor = derecho
            if menor == i:
                break
            self._datos[i], self._datos[menor] = self._datos[menor], self._datos[i]
            i = menor
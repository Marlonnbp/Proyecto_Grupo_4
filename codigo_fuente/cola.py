class Cola:
    def __init__(self):
        """Inicializa una cola vacía."""
        self._elementos = []

    def esta_vacia(self):
        """Devuelve True si la cola no tiene elementos, False en caso contrario."""
        return len(self._elementos) == 0

    def encolar(self, item):
        """Agrega un elemento al final de la cola (enqueue)."""
        self._elementos.append(item)

    def desencolar(self):
        """Remueve y devuelve el primer elemento de la cola (dequeue)."""
        if self.esta_vacia():
            raise IndexError("No se puede desencolar: la cola está vacía.")
        return self._elementos.pop(0)

    def frente(self):
        """Devuelve el primer elemento de la cola sin removerlo (peek/front)."""
        if self.esta_vacia():
            raise IndexError("La cola está vacía.")
        return self._elementos[0]

    def __len__(self):
        """Permite usar len() sobre la cola para obtener su tamaño."""
        return len(self._elementos)

    def __str__(self):
        """Representación en cadena para depuración."""
        return str(self._elementos)
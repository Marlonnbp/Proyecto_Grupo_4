from codigo_fuente.lista_enlazada import ListaEnlazada


class _Entrada:
    """Par (clave, sensor) almacenado dentro de cada cubeta de la tabla."""
    def __init__(self, clave, sensor):
        self.clave = clave
        self.sensor = sensor


class TablaHash:
    """Tabla hash con encadenamiento (chaining) implementada desde cero.

    - El arreglo principal contiene una ListaEnlazada propia por posición.
    - La clave es el ID_Sensor (por ejemplo "S01" o "S27").
    - Si el factor de carga supera FACTOR_CARGA_MAX, la tabla se redimensiona.
    """
    CAPACIDAD_INICIAL = 53        # número primo: reparte mejor los índices
    FACTOR_CARGA_MAX = 0.75
    _BASE = 31                    # base del hash polinómico

    def __init__(self, capacidad=CAPACIDAD_INICIAL):
        if capacidad < 1:
            raise ValueError("La capacidad debe ser al menos 1.")
        self._capacidad = capacidad
        self._cubetas = self._crear_cubetas(capacidad)
        self._tamano = 0

    # ------------------------------------------------------------------
    # Utilidades internas
    # ------------------------------------------------------------------
    @staticmethod
    def _crear_cubetas(capacidad):
        cubetas = [None] * capacidad
        for i in range(capacidad):
            cubetas[i] = ListaEnlazada()
        return cubetas

    def _hash(self, clave):
        """Función de dispersión polinómica: convierte el ID en un índice.

        h = (h * 31 + código_del_carácter) mod capacidad
        Ejemplo: "S01" y "S27" producen índices distintos dentro de [0, capacidad).
        """
        clave = str(clave)
        valor = 0
        for caracter in clave:
            valor = (valor * self._BASE + ord(caracter)) % self._capacidad
        return valor

    def _buscar_entrada(self, clave):
        clave = str(clave)
        for entrada in self._cubetas[self._hash(clave)]:
            if entrada.clave == clave:
                return entrada
        return None

    def _redimensionar(self):
        """Duplica la capacidad y reubica todas las entradas (rehash)."""
        entradas = []
        for cubeta in self._cubetas:
            for entrada in cubeta:
                entradas.append(entrada)

        self._capacidad = self._capacidad * 2 + 1
        self._cubetas = self._crear_cubetas(self._capacidad)
        for entrada in entradas:
            self._cubetas[self._hash(entrada.clave)].agregar_al_final(entrada)

    # ------------------------------------------------------------------
    # Operaciones públicas
    # ------------------------------------------------------------------
    def insertar(self, clave, sensor):
        """Inserta el sensor con su ID. Si la clave ya existe, actualiza el sensor."""
        clave = str(clave)
        existente = self._buscar_entrada(clave)
        if existente is not None:
            existente.sensor = sensor
            return

        if (self._tamano + 1) / self._capacidad > self.FACTOR_CARGA_MAX:
            self._redimensionar()

        self._cubetas[self._hash(clave)].agregar_al_final(_Entrada(clave, sensor))
        self._tamano += 1

    def buscar(self, clave):
        """Devuelve el sensor asociado al ID, o None si no existe."""
        entrada = self._buscar_entrada(clave)
        return entrada.sensor if entrada is not None else None

    def contiene(self, clave):
        return self._buscar_entrada(clave) is not None

    def obtener_tamano(self):
        return self._tamano

    def obtener_capacidad(self):
        return self._capacidad

    def factor_carga(self):
        return self._tamano / self._capacidad

    def claves(self):
        """Generador de todos los IDs almacenados."""
        for cubeta in self._cubetas:
            for entrada in cubeta:
                yield entrada.clave

    def __len__(self):
        return self._tamano

    def __contains__(self, clave):
        return self.contiene(clave)

    def __iter__(self):
        """Recorre todos los sensores almacenados."""
        for cubeta in self._cubetas:
            for entrada in cubeta:
                yield entrada.sensor

    def __repr__(self):
        return (f"TablaHash(tamano={self._tamano}, capacidad={self._capacidad}, "
                f"carga={self.factor_carga():.2f})")
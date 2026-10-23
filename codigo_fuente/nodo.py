class NodoLista:
    """Nodo genérico para la Lista Enlazada dinámica."""
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None


class NodoSensor:
    """Nodo del Grafo que representa una estación sísmica del territorio peruano."""
    def __init__(self, id_sensor, ciudad, latitud, longitud, altitud, interferencia_rf, tipo_suelo):
        self.id = str(id_sensor)
        self.ciudad = str(ciudad)
        self.latitud = float(latitud)
        self.longitud = float(longitud)
        self.altitud = float(altitud)
        self.interferencia_rf = int(interferencia_rf)
        self.tipo_suelo = int(tipo_suelo)  # 1: roca, 2: arena, 3: arcilla
        self.estado = "Reposo"             # Estado inicial según el autómata

    def __repr__(self):
        return f"Sensor({self.id}, {self.ciudad}, Suelo: {self.tipo_suelo}, Estado: {self.estado})"
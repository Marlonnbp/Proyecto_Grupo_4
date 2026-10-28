from codigo_fuente.nodo import NodoSensor
from codigo_fuente.arista import Arista
from codigo_fuente.lista_enlazada import ListaEnlazada


class Grafo:
    def __init__(self):
        self.vertices = ListaEnlazada()
        self.aristas = ListaEnlazada()
        self.adyacencias = {}

    def agregar_vertice(self, sensor: NodoSensor):
        if sensor.id not in self.adyacencias:
            self.vertices.agregar_al_final(sensor)
            self.adyacencias[sensor.id] = ListaEnlazada()

    def agregar_arista(self, id_u, id_v, costo):
        if id_u not in self.adyacencias or id_v not in self.adyacencias:
            raise ValueError(f"Sensor inexistente: {id_u} o {id_v}")
        if id_u == id_v:
            raise ValueError(f"Un sensor no puede enlazarse consigo mismo: {id_u}")

        menor, mayor = sorted((id_u, id_v))
        arista_directa = Arista(menor, mayor, costo)
        arista_inversa = Arista(mayor, menor, costo)

        self.adyacencias[menor].agregar_al_final(arista_directa)
        self.adyacencias[mayor].agregar_al_final(arista_inversa)
        self.aristas.agregar_al_final(arista_directa)

    def obtener_sensor(self, id_sensor):
        for sensor in self.vertices:
            if sensor.id == id_sensor:
                return sensor
        return None

    def obtener_vecinos(self, id_sensor):
        return self.adyacencias.get(id_sensor, ListaEnlazada())

    def cantidad_vertices(self):
        return self.vertices.obtener_tamano()

    def cantidad_aristas(self):
        return self.aristas.obtener_tamano()
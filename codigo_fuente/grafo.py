from nodo import NodoSensor
from arista import Arista
from lista_enlazada import ListaEnlazada

class Grafo:
    def __init__(self):
        self.vertices = ListaEnlazada()  # ListaEnlazada de NodoSensor
        self.aristas = ListaEnlazada()   # ListaEnlazada de Arista
        self.adyacencias = {}            # Dict interno: id_sensor -> ListaEnlazada de Aristas

    def agregar_vertice(self, sensor: NodoSensor):
        if sensor.id not in self.adyacencias:
            self.vertices.agregar_al_final(sensor)
            self.adyacencias[sensor.id] = ListaEnlazada()

    def agregar_arista(self, id_u, id_v, costo):
        if id_u in self.adyacencias and id_v in self.adyacencias:
            arista_u_v = Arista(id_u, id_v, costo)
            arista_v_u = Arista(id_v, id_u, costo)

            self.adyacencias[id_u].agregar_al_final(arista_u_v)
            self.adyacencias[id_v].agregar_al_final(arista_v_u)
            self.aristas.agregar_al_final(arista_u_v)

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
import unittest

from codigo_fuente.grafo import Grafo
from codigo_fuente.kruskal import kruskal
from codigo_fuente.nodo import NodoSensor


def crear_grafo(ids, enlaces):
    grafo = Grafo()
    for id_sensor in ids:
        grafo.agregar_vertice(NodoSensor(id_sensor, 'Ciudad', 0.0, 0.0, 0.0, 5, 1))
    for u, v, costo in enlaces:
        grafo.agregar_arista(u, v, costo)
    return grafo


class TestKruskal(unittest.TestCase):
    def test_ejemplo_del_documento(self):
        ids = ['S01', 'S02', 'S03', 'S04', 'S05']
        enlaces = [
            ('S01', 'S02', 20), ('S01', 'S03', 30), ('S01', 'S04', 38), ('S01', 'S05', 75),
            ('S02', 'S03', 12), ('S02', 'S04', 26), ('S02', 'S05', 62),
            ('S03', 'S04', 15), ('S03', 'S05', 52),
            ('S04', 'S05', 40),
        ]
        arbol, total = kruskal(crear_grafo(ids, enlaces))
        pares = sorted((a.origen, a.destino) for a in arbol)
        self.assertEqual(pares, [('S01', 'S02'), ('S02', 'S03'), ('S03', 'S04'), ('S04', 'S05')])
        self.assertEqual(arbol.obtener_tamano(), 4)
        self.assertEqual(total, 87)

    def test_desempate_por_identificador(self):
        enlaces = [('S02', 'S03', 5), ('S01', 'S03', 5), ('S01', 'S02', 5)]
        arbol, total = kruskal(crear_grafo(['S01', 'S02', 'S03'], enlaces))
        pares = [(a.origen, a.destino) for a in arbol]
        self.assertEqual(pares, [('S01', 'S02'), ('S01', 'S03')])
        self.assertEqual(total, 10)

    def test_grafo_no_conexo_devuelve_bosque(self):
        enlaces = [('S01', 'S02', 3), ('S03', 'S04', 4)]
        arbol, total = kruskal(crear_grafo(['S01', 'S02', 'S03', 'S04'], enlaces))
        self.assertLess(arbol.obtener_tamano(), 3)
        self.assertEqual(total, 7)

    def test_un_solo_sensor(self):
        arbol, total = kruskal(crear_grafo(['S01'], []))
        self.assertEqual(arbol.obtener_tamano(), 0)
        self.assertEqual(total, 0)


if __name__ == '__main__':
    unittest.main()
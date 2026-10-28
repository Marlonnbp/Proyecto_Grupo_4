import unittest
from codigo_fuente.grafo import Grafo
from codigo_fuente.nodo import NodoSensor
from codigo_fuente.recorridos import bfs_saltos

class TestRecorridos(unittest.TestCase):
    
    def setUp(self):
        self.grafo = Grafo()
        self.s1 = NodoSensor("S01", "Lima", -12.0, -77.0, 10, 5, 2)
        self.s2 = NodoSensor("S02", "Callao", -12.1, -77.1, 5, 5, 2)
        self.s3 = NodoSensor("S03", "Ica", -14.0, -75.7, 100, 4, 2)
        self.s4 = NodoSensor("S04", "Pisco", -13.7, -76.2, 20, 4, 2)
        
        for s in [self.s1, self.s2, self.s3, self.s4]:
            self.grafo.agregar_vertice(s)
            
        self.grafo.agregar_arista("S01", "S02", 10.0)
        self.grafo.agregar_arista("S02", "S03", 15.0)
        self.grafo.agregar_arista("S03", "S04", 12.0)

    def test_bfs_saltos(self):
        distancias = bfs_saltos(self.grafo, "S01")
        self.assertEqual(distancias["S01"], 0)
        self.assertEqual(distancias["S02"], 1)
        self.assertEqual(distancias["S03"], 2)
        self.assertEqual(distancias["S04"], 3)

if __name__ == "__main__":
    unittest.main()
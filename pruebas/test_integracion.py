import os
import unittest

from codigo_fuente.carga_datos import cargar_datos_csv
from codigo_fuente.costos import calcular_costos_enlaces, cantidad_enlaces
from codigo_fuente.grafo import Grafo
from codigo_fuente.kruskal import kruskal
from codigo_fuente.verificador import verificar_arbol

RUTA_CSV = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', 'datos', 'sensores_sismicos_peru.csv'
)


class TestIntegracion27Sensores(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grafo = Grafo()
        cargar_datos_csv(RUTA_CSV, cls.grafo)
        for id_u, id_v, costo in calcular_costos_enlaces(cls.grafo.vertices):
            cls.grafo.agregar_arista(id_u, id_v, costo)

    def test_cantidad_de_sensores_y_enlaces(self):
        self.assertEqual(self.grafo.cantidad_vertices(), 27)
        self.assertEqual(self.grafo.cantidad_aristas(), cantidad_enlaces(27))
        self.assertEqual(self.grafo.cantidad_aristas(), 351)

    def test_red_base_es_arbol_valido(self):
        arbol, total = kruskal(self.grafo)
        resultado = verificar_arbol(self.grafo, arbol)
        self.assertEqual(arbol.obtener_tamano(), 26)
        self.assertTrue(resultado['valido'])
        self.assertAlmostEqual(resultado['costo_total'], total)


if __name__ == '__main__':
    unittest.main()
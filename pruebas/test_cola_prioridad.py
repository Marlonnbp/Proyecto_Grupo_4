import random
import unittest

from codigo_fuente.arista import Arista
from codigo_fuente.cola_prioridad import ColaPrioridad


class TestColaPrioridad(unittest.TestCase):
    def test_extrae_en_orden_ascendente(self):
        cola = ColaPrioridad()
        for valor in [5, 3, 8, 1, 9, 2]:
            cola.insertar(valor)
        resultado = [cola.extraer_minimo() for _ in range(6)]
        self.assertEqual(resultado, [1, 2, 3, 5, 8, 9])

    def test_cola_vacia_lanza_error(self):
        cola = ColaPrioridad()
        self.assertTrue(cola.esta_vacia())
        with self.assertRaises(IndexError):
            cola.extraer_minimo()
        with self.assertRaises(IndexError):
            cola.ver_minimo()

    def test_ver_minimo_no_extrae(self):
        cola = ColaPrioridad()
        cola.insertar(4)
        cola.insertar(2)
        self.assertEqual(cola.ver_minimo(), 2)
        self.assertEqual(cola.obtener_tamano(), 2)

    def test_aristas_desempatan_por_identificador(self):
        cola = ColaPrioridad()
        cola.insertar(Arista('S02', 'S03', 5))
        cola.insertar(Arista('S01', 'S04', 5))
        cola.insertar(Arista('S01', 'S02', 5))
        orden = [(a.origen, a.destino) for a in (cola.extraer_minimo() for _ in range(3))]
        self.assertEqual(orden, [('S01', 'S02'), ('S01', 'S04'), ('S02', 'S03')])

    def test_tuplas_para_dijkstra(self):
        cola = ColaPrioridad()
        cola.insertar((4.0, 'S02'))
        cola.insertar((4.0, 'S01'))
        cola.insertar((1.0, 'S03'))
        self.assertEqual(cola.extraer_minimo(), (1.0, 'S03'))
        self.assertEqual(cola.extraer_minimo(), (4.0, 'S01'))
        self.assertEqual(cola.extraer_minimo(), (4.0, 'S02'))

    def test_orden_con_datos_aleatorios(self):
        random.seed(42)
        valores = [random.randint(0, 1000) for _ in range(200)]
        cola = ColaPrioridad()
        for valor in valores:
            cola.insertar(valor)
        resultado = [cola.extraer_minimo() for _ in range(len(valores))]
        self.assertEqual(resultado, sorted(valores))


if __name__ == '__main__':
    unittest.main()
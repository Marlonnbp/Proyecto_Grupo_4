import unittest

from codigo_fuente.arista import Arista
from codigo_fuente.grafo import Grafo
from codigo_fuente.lista_enlazada import ListaEnlazada
from codigo_fuente.nodo import NodoSensor
from codigo_fuente.verificador import verificar_arbol, verificar_red_operativa


def crear_grafo(ids):
    grafo = Grafo()
    for id_sensor in ids:
        grafo.agregar_vertice(NodoSensor(id_sensor, 'Ciudad', 0.0, 0.0, 0.0, 5, 1))
    return grafo


def crear_lista(*aristas):
    lista = ListaEnlazada()
    for arista in aristas:
        lista.agregar_al_final(arista)
    return lista


class TestVerificador(unittest.TestCase):
    def setUp(self):
        self.grafo = crear_grafo(['S01', 'S02', 'S03', 'S04'])

    def test_arbol_valido(self):
        arbol = crear_lista(Arista('S01', 'S02', 5), Arista('S02', 'S03', 7), Arista('S03', 'S04', 3))
        resultado = verificar_arbol(self.grafo, arbol)
        self.assertTrue(resultado['valido'])
        self.assertEqual(resultado['aristas_esperadas'], 3)
        self.assertEqual(resultado['aristas_obtenidas'], 3)
        self.assertTrue(resultado['conexo'])
        self.assertTrue(resultado['sin_ciclos'])
        self.assertEqual(resultado['costo_total'], 15)

    def test_arbol_con_ciclo_y_nodo_aislado(self):
        arbol = crear_lista(Arista('S01', 'S02', 5), Arista('S02', 'S03', 7), Arista('S01', 'S03', 3))
        resultado = verificar_arbol(self.grafo, arbol)
        self.assertEqual(resultado['aristas_obtenidas'], 3)
        self.assertFalse(resultado['conexo'])
        self.assertFalse(resultado['sin_ciclos'])
        self.assertFalse(resultado['valido'])

    def test_arbol_con_arista_faltante(self):
        arbol = crear_lista(Arista('S01', 'S02', 5), Arista('S02', 'S03', 7))
        resultado = verificar_arbol(self.grafo, arbol)
        self.assertFalse(resultado['conexo'])
        self.assertTrue(resultado['sin_ciclos'])
        self.assertFalse(resultado['valido'])

    def test_red_operativa_conexa_con_respaldo(self):
        aristas = crear_lista(
            Arista('S01', 'S02', 5), Arista('S02', 'S03', 7),
            Arista('S03', 'S04', 3), Arista('S01', 'S04', 9),
        )
        resultado = verificar_red_operativa(self.grafo, aristas)
        self.assertTrue(resultado['conexa'])
        self.assertEqual(resultado['aristas'], 4)
        self.assertEqual(resultado['costo_total'], 24)

    def test_red_operativa_no_conexa(self):
        aristas = crear_lista(Arista('S01', 'S02', 5), Arista('S03', 'S04', 3))
        self.assertFalse(verificar_red_operativa(self.grafo, aristas)['conexa'])


if __name__ == '__main__':
    unittest.main()
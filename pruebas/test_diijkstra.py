import unittest

from codigo_fuente.grafo import Grafo
from codigo_fuente.dijkstra import dijkstra, ruta_optima, crear_calcular_ruta
from codigo_fuente.simulacion_alerta import SimuladorAlerta


class SensorFalso:
    def __init__(self, id):
        self.id = id


def construir_grafo(ids, enlaces):
    g = Grafo()
    for i in ids:
        g.agregar_vertice(SensorFalso(i))
    for u, v, costo in enlaces:
        g.agregar_arista(u, v, costo)
    return g


def red_operativa_ejemplo():
    return construir_grafo(
        ["S01", "S02", "S03", "S04", "S05"],
        [("S02", "S03", 12), ("S03", "S04", 15), ("S01", "S02", 20),
         ("S04", "S05", 40), ("S01", "S04", 38)],
    )


class TestDijkstra(unittest.TestCase):
    def test_ejemplo_seccion_1_5(self):
        ruta, costo = ruta_optima(red_operativa_ejemplo(), "S05", "S01")
        self.assertEqual(ruta, ["S05", "S04", "S01"])
        self.assertEqual(costo, 78)
        self.assertEqual(len(ruta) - 1, 2)  # saltos

    def test_sin_respaldo_usa_el_arbol(self):
        g = construir_grafo(
            ["S01", "S02", "S03", "S04", "S05"],
            [("S02", "S03", 12), ("S03", "S04", 15), ("S01", "S02", 20),
             ("S04", "S05", 40)],
        )
        ruta, costo = ruta_optima(g, "S05", "S01")
        self.assertEqual(ruta, ["S05", "S04", "S03", "S02", "S01"])
        self.assertEqual(costo, 87)

    def test_origen_igual_destino(self):
        ruta, costo = ruta_optima(red_operativa_ejemplo(), "S01", "S01")
        self.assertEqual(ruta, ["S01"])
        self.assertEqual(costo, 0)

    def test_distancias_completas(self):
        dist, _ = dijkstra(red_operativa_ejemplo(), "S01")
        self.assertEqual(dist.buscar("S02"), 20)
        self.assertEqual(dist.buscar("S03"), 32)
        self.assertEqual(dist.buscar("S04"), 38)
        self.assertEqual(dist.buscar("S05"), 78)

    def test_sensor_aislado_sin_ruta(self):
        g = construir_grafo(["A", "B", "C"], [("A", "B", 5)])
        self.assertIsNone(ruta_optima(g, "A", "C"))

    def test_origen_inexistente(self):
        with self.assertRaises(KeyError):
            dijkstra(red_operativa_ejemplo(), "X")

    def test_costo_no_positivo(self):
        with self.assertRaises(ValueError):
            construir_grafo(["A", "B"], [("A", "B", 0)])

    def test_costos_decimales(self):
        g = construir_grafo(["A", "B", "C"],
                            [("A", "B", 1.5), ("B", "C", 2.25), ("A", "C", 5.0)])
        ruta, costo = ruta_optima(g, "A", "C")
        self.assertEqual(ruta, ["A", "B", "C"])
        self.assertAlmostEqual(costo, 3.75)


class TestIntegracionConSimulador(unittest.TestCase):
    def test_evento_completo(self):
        g = red_operativa_ejemplo()
        sensores = [("S01", 2), ("S02", 2), ("S03", 2), ("S04", 1), ("S05", 1)]
        sim = SimuladorAlerta(sensores, crear_calcular_ruta(g))
        r = sim.simular_evento("S05", 6.2, "S01")
        self.assertTrue(r.propagada)
        self.assertEqual(r.costo_total, 78)
        self.assertEqual(r.saltos, 2)
        self.assertEqual(r.alertados, ["S05", "S04", "S01"])


if __name__ == "__main__":
    unittest.main()
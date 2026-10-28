#favian

import unittest

from pila import Pila
from automata_sensor import (
    AutomataSensor, REPOSO, VIGILANCIA, ALERTA, umbral_de_suelo,
)
from simulacion_alerta import SimuladorAlerta, reconstruir_ruta


class TestPila(unittest.TestCase):
    def test_lifo(self):
        p = Pila()
        for x in (1, 2, 3):
            p.apilar(x)
        self.assertEqual(len(p), 3)
        self.assertEqual(p.ver_tope(), 3)
        self.assertEqual([p.desapilar() for _ in range(3)], [3, 2, 1])
        self.assertTrue(p.esta_vacia())

    def test_vacia_lanza_error(self):
        p = Pila()
        with self.assertRaises(IndexError):
            p.desapilar()
        with self.assertRaises(IndexError):
            p.ver_tope()


class TestAutomata(unittest.TestCase):
    def test_umbrales(self):
        self.assertGreater(umbral_de_suelo(1), umbral_de_suelo(2))
        self.assertGreaterEqual(umbral_de_suelo(2), umbral_de_suelo(3))
        with self.assertRaises(ValueError):
            umbral_de_suelo(9)

    def test_reposo(self):
        a = AutomataSensor("S", 1)  # umbral 5.5
        self.assertEqual(a.procesar("d", 5.4), VIGILANCIA)
        a = AutomataSensor("S", 1)
        self.assertEqual(a.procesar("d", 5.5), ALERTA)
        a = AutomataSensor("S", 1)
        self.assertEqual(a.procesar("r"), ALERTA)
        a = AutomataSensor("S", 1)
        self.assertEqual(a.procesar("t"), REPOSO)

    def test_vigilancia(self):
        a = AutomataSensor("S", 1)
        a.procesar("d", 3)
        self.assertEqual(a.procesar("d", 4), VIGILANCIA)
        self.assertEqual(a.procesar("t"), REPOSO)
        a.procesar("d", 3)
        self.assertEqual(a.procesar("d", 6), ALERTA)
        a.procesar("t")
        a.procesar("d", 3)
        self.assertEqual(a.procesar("r"), ALERTA)

    def test_alerta_ignora_d_y_r(self):
        a = AutomataSensor("S", 1)
        a.procesar("r")
        self.assertEqual(a.procesar("d", 1), ALERTA)
        self.assertEqual(a.procesar("r"), ALERTA)
        self.assertEqual(a.procesar("t"), REPOSO)

    def test_entradas_invalidas(self):
        a = AutomataSensor("S", 1)
        with self.assertRaises(ValueError):
            a.procesar("x")
        with self.assertRaises(ValueError):
            a.procesar("d")  # falta magnitud


class TestReconstruirRuta(unittest.TestCase):
    def test_ruta(self):
        pred = {"S05": None, "S04": "S05", "S01": "S04"}
        self.assertEqual(reconstruir_ruta(pred, "S05", "S01"), ["S05", "S04", "S01"])

    def test_origen_igual_destino(self):
        self.assertEqual(reconstruir_ruta({"S01": None}, "S01", "S01"), ["S01"])

    def test_sin_camino(self):
        pred = {"S01": None, "S02": None}
        self.assertIsNone(reconstruir_ruta(pred, "S01", "S02"))


class TestSimulador(unittest.TestCase):
    """Reproduce el ejemplo de la sección 1.5 con una ruta simulada."""

    def setUp(self):
        sensores = [("S01", 2), ("S02", 2), ("S03", 2), ("S04", 1), ("S05", 1)]
        self.llamadas = []

        def ruta_falsa(origen, destino):
            self.llamadas.append((origen, destino))
            return ["S05", "S04", "S01"], 78

        self.sim = SimuladorAlerta(sensores, ruta_falsa)

    def test_evento_que_alerta(self):
        r = self.sim.simular_evento("S05", 6.2, "S01")
        self.assertTrue(r.propagada)
        self.assertEqual(r.costo_total, 78)
        self.assertEqual(r.saltos, 2)
        self.assertEqual(r.alertados, ["S05", "S04", "S01"])
        self.assertEqual(self.sim.automata("S01").estado, ALERTA)
        self.assertEqual(self.sim.automata("S02").estado, REPOSO)

    def test_evento_bajo_umbral_no_propaga(self):
        r = self.sim.simular_evento("S05", 4.0, "S01")
        self.assertFalse(r.propagada)
        self.assertEqual(self.sim.automata("S05").estado, VIGILANCIA)
        self.assertEqual(self.llamadas, [])  # ni se calcula la ruta
        self.assertEqual(self.sim.automata("S04").estado, REPOSO)

    def test_reinicio_entre_eventos(self):
        self.sim.simular_evento("S05", 6.2, "S01")
        self.sim.simular_evento("S05", 4.0, "S01")
        self.assertEqual(self.sim.automata("S01").estado, REPOSO)

    def test_ids_invalidos(self):
        with self.assertRaises(KeyError):
            self.sim.simular_evento("X", 6, "S01")
        with self.assertRaises(KeyError):
            self.sim.simular_evento("S05", 6, "X")

    def test_sin_ruta(self):
        sim = SimuladorAlerta([("A", 1), ("B", 1)], lambda o, d: None)
        r = sim.simular_evento("A", 7, "B")
        self.assertFalse(r.propagada)
        self.assertEqual(r.alertados, ["A"])

    def test_reporte_imprimible(self):
        texto = str(self.sim.simular_evento("S05", 6.2, "S01"))
        self.assertIn("Costo total", texto)


if __name__ == "__main__":
    unittest.main()

import os
import tempfile
import unittest

from codigo_fuente import costos
from codigo_fuente.generador_datos import generar_dataset
from codigo_fuente.lista_enlazada import ListaEnlazada
from codigo_fuente.modelo_mlp import ModeloCostoMLP, cargar_o_entrenar
from codigo_fuente.nodo import NodoSensor


def crear_sensores(n=27):
    sensores = ListaEnlazada()
    for i in range(n):
        sensores.agregar_al_final(NodoSensor(
            f"S{i + 1:02d}", f"Ciudad{i + 1}",
            -1.0 - i * 0.6, -80.0 + i * 0.4, 100 + i * 150, 1 + i % 10, 1 + i % 3))
    return sensores


class TestModeloMLP(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.datos = generar_dataset(2000)
        cls.entradas = [f[:3] for f in cls.datos]
        cls.salidas = [f[3] for f in cls.datos]
        cls.modelo = ModeloCostoMLP()
        cls.metricas = cls.modelo.entrenar(cls.entradas, cls.salidas)

    def test_sin_entrenar_lanza_error(self):
        with self.assertRaises(RuntimeError):
            ModeloCostoMLP().predecir_costo(100, 100, 5)

    def test_metricas_presentes(self):
        for nombre in ("mlp", "lineal"):
            for clave in ("mae", "rmse", "r2"):
                self.assertIn(clave, self.metricas[nombre])
        self.assertEqual(self.metricas["n_prueba"], 400)

    def test_mlp_mejora_a_la_formula_lineal(self):
        self.assertLess(self.metricas["mlp"]["mae"], self.metricas["lineal"]["mae"])
        self.assertGreater(self.metricas["mlp"]["r2"], 0.95)

    def test_prediccion_cercana_a_la_formula(self):
        costo = self.modelo.predecir_costo(500, 1000, 5)
        referencia = costos.costo_lineal(500, 1000, 5)
        self.assertLess(abs(costo - referencia) / referencia, 0.25)

    def test_misma_semilla_mismo_modelo(self):
        a, b = ModeloCostoMLP(), ModeloCostoMLP()
        a.entrenar(self.entradas[:600], self.salidas[:600])
        b.entrenar(self.entradas[:600], self.salidas[:600])
        self.assertEqual(a.predecir_costo(300, 500, 4), b.predecir_costo(300, 500, 4))

    def test_guardar_y_cargar(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = os.path.join(carpeta, "modelo.pkl")
            self.modelo.guardar(ruta)
            cargado = ModeloCostoMLP.cargar(ruta)
        self.assertEqual(cargado.predecir_costo(300, 500, 4),
                         self.modelo.predecir_costo(300, 500, 4))

    def test_351_costos_para_27_sensores(self):
        enlaces = self.modelo.predecir_costos_enlaces(crear_sensores(27))
        self.assertEqual(enlaces.obtener_tamano(), 351)
        for _, _, costo in enlaces:
            self.assertGreaterEqual(costo, costos.COSTO_MINIMO)

    def test_simetria_del_costo_mlp(self):
        a = NodoSensor("S01", "Lima", -12.05, -77.04, 150, 3, 1)
        b = NodoSensor("S05", "Arequipa", -16.40, -71.54, 2335, 8, 1)
        self.assertEqual(self.modelo.costo_sensores(a, b), self.modelo.costo_sensores(b, a))

    def test_respaldo_con_modelo_sin_entrenar(self):
        a = NodoSensor("S01", "Lima", -12.05, -77.04, 150, 3, 1)
        b = NodoSensor("S05", "Arequipa", -16.40, -71.54, 2335, 8, 1)
        sin_entrenar = ModeloCostoMLP()
        self.assertEqual(sin_entrenar.costo_sensores(a, b), costos.calcular_costo(a, b))

    def test_cargar_o_entrenar_crea_y_reutiliza_el_modelo(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta_modelo = os.path.join(carpeta, "modelo.pkl")
            ruta_datos = os.path.join(carpeta, "datos.csv")
            primero = cargar_o_entrenar(ruta_modelo, ruta_datos)
            self.assertTrue(os.path.exists(ruta_modelo))
            self.assertTrue(os.path.exists(ruta_datos))
            segundo = cargar_o_entrenar(ruta_modelo, ruta_datos)
            self.assertEqual(primero.predecir_costo(300, 500, 4),
                             segundo.predecir_costo(300, 500, 4))

    def test_modelo_dañado_se_reentrena(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta_modelo = os.path.join(carpeta, "modelo.pkl")
            ruta_datos = os.path.join(carpeta, "datos.csv")
            with open(ruta_modelo, "wb") as archivo:
                archivo.write(b"no es un modelo")
            modelo = cargar_o_entrenar(ruta_modelo, ruta_datos)
            self.assertTrue(modelo.entrenado)


if __name__ == "__main__":
    unittest.main()
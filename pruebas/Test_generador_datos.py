import os
import tempfile
import unittest

from codigo_fuente import generador_datos as gd


class TestGeneradorDatos(unittest.TestCase):

    def test_misma_semilla_mismos_datos(self):
        self.assertEqual(gd.generar_dataset(500), gd.generar_dataset(500))

    def test_otra_semilla_datos_distintos(self):
        self.assertNotEqual(gd.generar_dataset(100, semilla=1),
                            gd.generar_dataset(100, semilla=2))

    def test_cantidad_y_columnas(self):
        filas = gd.generar_dataset(200)
        self.assertEqual(len(filas), 200)
        self.assertTrue(all(len(f) == 4 for f in filas))

    def test_rangos_validos(self):
        for dist, dalt, interf, costo in gd.generar_dataset(1000):
            self.assertGreaterEqual(dist, 0)
            self.assertGreaterEqual(dalt, 0)
            self.assertGreaterEqual(interf, 1)
            self.assertLessEqual(interf, 10)
            self.assertGreaterEqual(costo, gd.COSTO_MINIMO)

    def test_haversine_lima_arequipa(self):
        # Lima (-12.05, -77.04) a Arequipa (-16.40, -71.54): unos 760 km
        d = gd.haversine(-12.05, -77.04, -16.40, -71.54)
        self.assertGreater(d, 700)
        self.assertLess(d, 820)

    def test_guardar_y_cargar_csv(self):
        filas = gd.generar_dataset(50)
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = os.path.join(carpeta, "datos.csv")
            gd.guardar_csv(filas, ruta)
            entradas, salidas = gd.cargar_csv(ruta)
        self.assertEqual(len(entradas), 50)
        self.assertEqual(salidas, [f[3] for f in filas])
        self.assertEqual(entradas[0], filas[0][:3])


if __name__ == "__main__":
    unittest.main()
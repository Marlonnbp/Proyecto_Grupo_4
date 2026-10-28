import unittest

from codigo_fuente.nodo import NodoSensor
from codigo_fuente.tabla_hash import TablaHash


def crear_sensor(id_sensor, ciudad="Ciudad"):
    return NodoSensor(id_sensor, ciudad, -12.0, -77.0, 100, 5, 1)


class TestTablaHash(unittest.TestCase):

    def test_insertar_y_buscar(self):
        tabla = TablaHash()
        s01 = crear_sensor("S01", "Lima")
        tabla.insertar("S01", s01)
        self.assertIs(tabla.buscar("S01"), s01)
        self.assertEqual(len(tabla), 1)

    def test_buscar_inexistente_devuelve_none(self):
        tabla = TablaHash()
        self.assertIsNone(tabla.buscar("S99"))

    def test_indice_dentro_de_capacidad(self):
        tabla = TablaHash()
        for i in range(1, 28):
            indice = tabla._hash(f"S{i:02d}")
            self.assertGreaterEqual(indice, 0)
            self.assertLess(indice, tabla.obtener_capacidad())

    def test_hash_es_determinista(self):
        tabla = TablaHash()
        self.assertEqual(tabla._hash("S01"), tabla._hash("S01"))

    def test_colisiones_con_encadenamiento(self):
        # Capacidad 1 fuerza que todas las claves caigan en la misma cubeta.
        tabla = TablaHash(capacidad=1)
        tabla.FACTOR_CARGA_MAX = 1000  # evita redimensionar durante la prueba
        sensores = {f"S{i:02d}": crear_sensor(f"S{i:02d}") for i in range(1, 6)}
        for clave, sensor in sensores.items():
            tabla.insertar(clave, sensor)
        self.assertEqual(tabla._cubetas[0].obtener_tamano(), 5)
        for clave, sensor in sensores.items():
            self.assertIs(tabla.buscar(clave), sensor)

    def test_clave_duplicada_actualiza(self):
        tabla = TablaHash()
        original = crear_sensor("S01", "Lima")
        nuevo = crear_sensor("S01", "Lima Centro")
        tabla.insertar("S01", original)
        tabla.insertar("S01", nuevo)
        self.assertEqual(len(tabla), 1)
        self.assertIs(tabla.buscar("S01"), nuevo)

    def test_redimensionar_conserva_datos(self):
        tabla = TablaHash(capacidad=3)
        capacidad_inicial = tabla.obtener_capacidad()
        sensores = {f"S{i:02d}": crear_sensor(f"S{i:02d}") for i in range(1, 28)}
        for clave, sensor in sensores.items():
            tabla.insertar(clave, sensor)
        self.assertGreater(tabla.obtener_capacidad(), capacidad_inicial)
        self.assertEqual(len(tabla), 27)
        for clave, sensor in sensores.items():
            self.assertIs(tabla.buscar(clave), sensor)
        self.assertLessEqual(tabla.factor_carga(), TablaHash.FACTOR_CARGA_MAX)

    def test_27_sensores(self):
        tabla = TablaHash()
        for i in range(1, 28):
            clave = f"S{i:02d}"
            tabla.insertar(clave, crear_sensor(clave))
        self.assertEqual(len(tabla), 27)
        self.assertEqual(sorted(tabla.claves()), [f"S{i:02d}" for i in range(1, 28)])
        self.assertEqual(len(list(tabla)), 27)

    def test_contiene(self):
        tabla = TablaHash()
        tabla.insertar("S05", crear_sensor("S05"))
        self.assertIn("S05", tabla)
        self.assertNotIn("S06", tabla)

    def test_capacidad_invalida(self):
        with self.assertRaises(ValueError):
            TablaHash(capacidad=0)


if __name__ == "__main__":
    unittest.main()
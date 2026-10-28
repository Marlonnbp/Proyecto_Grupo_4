import unittest
from codigo_fuente.cola import Cola

class TestCola(unittest.TestCase):
    
    def test_cola_vacia_inicial(self):
        cola = Cola()
        self.assertTrue(cola.esta_vacia())
        self.assertEqual(len(cola), 0)

    def test_encolar_y_frente(self):
        cola = Cola()
        cola.encolar("S01")
        cola.encolar("S02")
        self.assertFalse(cola.esta_vacia())
        self.assertEqual(len(cola), 2)
        self.assertEqual(cola.frente(), "S01")

    def test_desencolar(self):
        cola = Cola()
        cola.encolar("S01")
        cola.encolar("S02")
        
        elem = cola.desencolar()
        self.assertEqual(elem, "S01")
        self.assertEqual(len(cola), 1)
        self.assertEqual(cola.frente(), "S02")

    def test_excepcion_cola_vacia(self):
        cola = Cola()
        with self.assertRaises(IndexError):
            cola.desencolar()
        with self.assertRaises(IndexError):
            cola.frente()

if __name__ == "__main__":
    unittest.main()
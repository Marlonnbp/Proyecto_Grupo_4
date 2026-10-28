import unittest
from codigo_fuente.grafo import Grafo
from codigo_fuente.nodo import NodoSensor
from codigo_fuente.arista import Arista
from codigo_fuente.respaldos import seleccionar_respaldos

class TestRespaldos(unittest.TestCase):
    
    def test_seleccion_respaldos_rn05(self):
        grafo_base = Grafo()
        # Creamos 5 sensores en línea recta: S1 - S2 - S3 - S4 - S5
        ids = ["S01", "S02", "S03", "S04", "S05"]
        for i, s_id in enumerate(ids):
            grafo_base.agregar_vertice(NodoSensor(s_id, f"Ciudad_{i}", 0.0, 0.0, 10, 5, 2))
            
        # Árbol base (4 aristas consecutivas)
        grafo_base.agregar_arista("S01", "S02", 10.0)
        grafo_base.agregar_arista("S02", "S03", 10.0)
        grafo_base.agregar_arista("S03", "S04", 10.0)
        grafo_base.agregar_arista("S04", "S05", 10.0)
        
        # Aristas descartadas por Kruskal (candidatas a respaldo)
        aristas_descartadas = [
            Arista("S01", "S03", 5.0),   # 2 saltos (Se debe filtrar/excluir)
            Arista("S01", "S04", 20.0),  # 3 saltos (Válido)
            Arista("S01", "S05", 25.0)   # 4 saltos (Válido)
        ]
        
        respaldos = seleccionar_respaldos(grafo_base, aristas_descartadas, R=2)
        
        # S01-S03 debe ser descartado porque su distancia en el árbol es menor a 3 saltos
        ids_respaldos = {(r.origen, r.destino) for r in respaldos}
        
        self.assertNotIn(("S01", "S03"), ids_respaldos)
        self.assertIn(("S01", "S04"), ids_respaldos)
        self.assertIn(("S01", "S05"), ids_respaldos)

if __name__ == "__main__":
    unittest.main()
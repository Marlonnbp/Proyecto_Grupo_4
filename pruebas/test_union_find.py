import unittest

from codigo_fuente.union_find import UnionFind


class TestUnionFind(unittest.TestCase):
    def setUp(self):
        self.ids = ['S01', 'S02', 'S03', 'S04', 'S05']
        self.uf = UnionFind(self.ids)

    def test_cada_elemento_inicia_en_su_propio_grupo(self):
        for id_sensor in self.ids:
            self.assertEqual(self.uf.find(id_sensor), id_sensor)

    def test_union_une_grupos_distintos(self):
        self.assertTrue(self.uf.union('S01', 'S02'))
        self.assertEqual(self.uf.find('S01'), self.uf.find('S02'))

    def test_union_repetida_detecta_ciclo(self):
        self.uf.union('S01', 'S02')
        self.uf.union('S02', 'S03')
        self.assertFalse(self.uf.union('S01', 'S03'))

    def test_grupos_separados_no_se_mezclan(self):
        self.uf.union('S01', 'S02')
        self.uf.union('S03', 'S04')
        self.assertNotEqual(self.uf.find('S01'), self.uf.find('S03'))
        self.assertEqual(self.uf.find('S05'), 'S05')

    def test_union_por_rango_cuelga_el_arbol_menor(self):
        self.uf.union('S01', 'S02')
        self.uf.union('S03', 'S01')
        self.assertEqual(self.uf.padre['S03'], 'S01')
        self.assertEqual(self.uf.rango['S01'], 1)

    def test_compresion_de_caminos(self):
        self.uf.union('S01', 'S02')
        self.uf.union('S03', 'S04')
        self.uf.union('S01', 'S03')
        self.assertEqual(self.uf.padre['S04'], 'S03')
        self.assertEqual(self.uf.find('S04'), 'S01')
        self.assertEqual(self.uf.padre['S04'], 'S01')

    def test_elemento_inexistente_lanza_error(self):
        with self.assertRaises(ValueError):
            self.uf.find('S99')


if __name__ == '__main__':
    unittest.main()
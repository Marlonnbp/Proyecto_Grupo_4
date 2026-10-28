class UnionFind:
    def _init_(self, ids):
        # Usamos diccionarios para mapear directamente el ID del sensor a su padre y rango
        self.padre = {}
        self.rango = {}
        
        for elem_id in ids:
            self.padre[elem_id] = elem_id
            self.rango[elem_id] = 0

    def find(self, elem_id):
        if self.padre[elem_id] != elem_id:
            # Compresión de caminos: el nodo apunta directamente a la raíz principal
            self.padre[elem_id] = self.find(self.padre[elem_id])
        return self.padre[elem_id]

    def union(self, a, b):
        raiz_a = self.find(a)
        raiz_b = self.find(b)

        # Si ya tienen la misma raíz, están en el mismo grupo (ciclo)
        if raiz_a == raiz_b:
            return False

        # Unión por rango: el árbol con menor altura se cuelga del de mayor altura
        if self.rango[raiz_a] < self.rango[raiz_b]:
            self.padre[raiz_a] = raiz_b
        elif self.rango[raiz_a] > self.rango[raiz_b]:
            self.padre[raiz_b] = raiz_a
        else:
            self.padre[raiz_b] = raiz_a
            self.rango[raiz_a] += 1

        return True
class UnionFind:
    def __init__(self, ids):
        self.padre = {}
        self.rango = {}
        for elem_id in ids:
            self.padre[elem_id] = elem_id
            self.rango[elem_id] = 0

    def find(self, elem_id):
        if elem_id not in self.padre:
            raise ValueError(f"Elemento inexistente: {elem_id}")
        if self.padre[elem_id] != elem_id:
            self.padre[elem_id] = self.find(self.padre[elem_id])
        return self.padre[elem_id]

    def union(self, a, b):
        raiz_a = self.find(a)
        raiz_b = self.find(b)

        if raiz_a == raiz_b:
            return False

        if self.rango[raiz_a] < self.rango[raiz_b]:
            self.padre[raiz_a] = raiz_b
        elif self.rango[raiz_a] > self.rango[raiz_b]:
            self.padre[raiz_b] = raiz_a
        else:
            self.padre[raiz_b] = raiz_a
            self.rango[raiz_a] += 1

        return True
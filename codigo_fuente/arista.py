class Arista:
    def __init__(self, origen, destino, costo):
        self.origen = str(origen)       # ID del sensor origen (ej: "S01")
        self.destino = str(destino)     # ID del sensor destino (ej: "S02")
        self.costo = float(costo)       # Costo positivo calculado por fórmula o MLP

    def __lt__(self, otra):
        if self.costo == otra.costo:
            return (self.origen, self.destino) < (otra.origen, otra.destino)
        return self.costo < otra.costo

    def __repr__(self):
        return f"Arista({self.origen} <--> {self.destino}, Costo: {self.costo:.2f})"
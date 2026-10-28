class Arista:
    def __init__(self, origen, destino, costo):
        self.origen = str(origen)
        self.destino = str(destino)
        self.costo = float(costo)
        if self.costo <= 0:
            raise ValueError(f"El costo debe ser positivo: {self.origen}-{self.destino} = {self.costo}")

    def __lt__(self, otra):
        if self.costo == otra.costo:
            return (self.origen, self.destino) < (otra.origen, otra.destino)
        return self.costo < otra.costo

    def __repr__(self):
        return f"Arista({self.origen} <--> {self.destino}, Costo: {self.costo:.2f})"
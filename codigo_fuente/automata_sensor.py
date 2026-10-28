#favian

"""Autómata de estados finitos de cada sensor (sección 2.3 del entregable).

Estados : Reposo, Vigilancia, Alerta
Entradas: d (evento sísmico con magnitud m), r (alerta recibida), t (reinicio)
"""

REPOSO = "Reposo"
VIGILANCIA = "Vigilancia"
ALERTA = "Alerta"

ENTRADA_D = "d"  # evento sísmico registrado en el sensor (lleva magnitud)
ENTRADA_R = "r"  # alerta recibida del sensor anterior en la ruta
ENTRADA_T = "t"  # reinicio

# Tipo de suelo (RN-01): 1 = roca, 2 = arena, 3 = arcilla.
# Menor umbral en suelos que amplifican las ondas (arena, arcilla).
# La roca usa 5.5, igual que el ejemplo de la sección 1.5.
# Valores ajustables tras las pruebas del grupo.
UMBRALES_POR_SUELO = {
    1: 5.5,  # roca
    2: 4.5,  # arena
    3: 4.0,  # arcilla
}


def umbral_de_suelo(tipo_suelo):
    if tipo_suelo not in UMBRALES_POR_SUELO:
        raise ValueError(f"Tipo de suelo inválido: {tipo_suelo!r} (use 1, 2 o 3)")
    return UMBRALES_POR_SUELO[tipo_suelo]


class AutomataSensor:
    """Un autómata por sensor. Implementa la tabla de transiciones de 2.3."""

    def __init__(self, id_sensor, tipo_suelo):
        self.id_sensor = id_sensor
        self.tipo_suelo = tipo_suelo
        self.umbral = umbral_de_suelo(tipo_suelo)
        self.estado = REPOSO

    def procesar(self, entrada, magnitud=None):
        """Aplica una entrada y devuelve el nuevo estado.

        - t: siempre vuelve a Reposo.
        - r: siempre pasa a Alerta (si ya estaba en Alerta se ignora).
        - d: requiere magnitud. Si estaba en Alerta, se ignora; si no,
             m >= umbral -> Alerta, m < umbral -> Vigilancia.
        """
        if entrada == ENTRADA_T:
            self.estado = REPOSO
        elif entrada == ENTRADA_R:
            self.estado = ALERTA
        elif entrada == ENTRADA_D:
            if magnitud is None:
                raise ValueError("La entrada 'd' requiere una magnitud")
            if self.estado != ALERTA:
                self.estado = ALERTA if magnitud >= self.umbral else VIGILANCIA
        else:
            raise ValueError(f"Entrada inválida: {entrada!r} (use 'd', 'r' o 't')")
        return self.estado

    def esta_en_alerta(self):
        return self.estado == ALERTA

    def __repr__(self):
        return f"AutomataSensor({self.id_sensor}, suelo={self.tipo_suelo}, estado={self.estado})"
from codigo_fuente.pila import Pila
from codigo_fuente.automata_sensor import (
    AutomataSensor, ALERTA, ENTRADA_D, ENTRADA_R, ENTRADA_T,
)


def reconstruir_ruta(predecesores, origen, destino):
    obtener = predecesores.buscar if hasattr(predecesores, "buscar") else predecesores.get
    pila = Pila()
    actual = destino
    while actual is not None:
        pila.apilar(actual)
        if actual == origen:
            break
        actual = obtener(actual)

    if pila.ver_tope() != origen:
        return None  

    ruta = []
    while not pila.esta_vacia():
        ruta.append(pila.desapilar())
    return ruta


class ReporteAlerta:

    def __init__(self, id_origen, magnitud, umbral, estado_origen):
        self.id_origen = id_origen
        self.magnitud = magnitud
        self.umbral = umbral
        self.estado_origen = estado_origen
        self.propagada = False
        self.ruta = []
        self.costo_total = 0
        self.saltos = 0
        self.alertados = []
        self.mensaje = ""

    def __str__(self):
        lineas = [
            "===== REPORTE DE ALERTA =====",
            f"Sensor del evento : {self.id_origen}",
            f"Magnitud          : {self.magnitud} (umbral del suelo: {self.umbral})",
            f"Estado del sensor : {self.estado_origen}",
        ]
        if self.propagada:
            lineas += [
                f"Ruta              : {' -> '.join(self.ruta)}",
                f"Costo total       : {self.costo_total}",
                f"Saltos            : {self.saltos}",
                f"Sensores alertados: {', '.join(self.alertados)}",
            ]
        if self.mensaje:
            lineas.append(self.mensaje)
        return "\n".join(lineas)


class SimuladorAlerta:

    def __init__(self, sensores, calcular_ruta):
        self._calcular_ruta = calcular_ruta
        self._automatas = {}
        for id_sensor, tipo_suelo in sensores:
            self._automatas[id_sensor] = AutomataSensor(id_sensor, tipo_suelo)

    def automata(self, id_sensor):
        return self._automatas[id_sensor]

    def reiniciar(self):
        for automata in self._automatas.values():
            automata.procesar(ENTRADA_T)

    def simular_evento(self, id_sensor, magnitud, id_sede):
        if id_sensor not in self._automatas:
            raise KeyError(f"Sensor inexistente: {id_sensor}")
        if id_sede not in self._automatas:
            raise KeyError(f"Sede central inexistente: {id_sede}")
        if magnitud < 0:
            raise ValueError("La magnitud no puede ser negativa")

        self.reiniciar()  

        origen = self._automatas[id_sensor]
        origen.procesar(ENTRADA_D, magnitud)
        reporte = ReporteAlerta(id_sensor, magnitud, origen.umbral, origen.estado)

        if not origen.esta_en_alerta():
            reporte.mensaje = "La magnitud no alcanza el umbral: no se propaga alerta."
            return reporte

        resultado = self._calcular_ruta(id_sensor, id_sede)
        if resultado is None:
            reporte.alertados = [id_sensor]
            reporte.mensaje = "No existe ruta hasta la sede central."
            return reporte

        ruta, costo = resultado
        reporte.propagada = True
        reporte.ruta = list(ruta)
        reporte.costo_total = costo
        reporte.saltos = len(ruta) - 1
        reporte.alertados = [id_sensor]

        for id_siguiente in ruta[1:]:
            siguiente = self._automatas[id_siguiente]
            if siguiente.estado != ALERTA:
                siguiente.procesar(ENTRADA_R)
                reporte.alertados.append(id_siguiente)
        return reporte

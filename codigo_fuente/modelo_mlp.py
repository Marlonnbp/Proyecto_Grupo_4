import os
import pickle

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

from codigo_fuente import costos
from codigo_fuente.generador_datos import (RUTA_DEFECTO, cargar_csv,
                                           generar_dataset, guardar_csv)
from codigo_fuente.lista_enlazada import ListaEnlazada
from codigo_fuente.nodo import NodoSensor

SEMILLA = 42
RUTA_MODELO = "datos/modelo_mlp.pkl"
CAPAS_OCULTAS = (32, 16)
FRACCION_PRUEBA = 0.2


class ModeloCostoMLP:
    """Red neuronal de regresión que estima el costo de un enlace."""

    def __init__(self, semilla=SEMILLA):
        self.semilla = semilla
        self.escalador_x = StandardScaler()
        self.escalador_y = StandardScaler()
        self.red = MLPRegressor(hidden_layer_sizes=CAPAS_OCULTAS,
                                activation="relu",
                                solver="adam",
                                max_iter=500,
                                early_stopping=True,
                                n_iter_no_change=20,
                                random_state=semilla)
        self.entrenado = False
        self.metricas = None

    # ------------------------------------------------------------------
    # Entrenamiento y evaluación
    # ------------------------------------------------------------------
    def entrenar(self, entradas, salidas):
        """Entrena con el 80 % de los datos y evalúa con el 20 % restante.

        entradas: filas [distancia_km, dif_altitud_m, interferencia_prom]
        salidas:  costo de cada fila
        Devuelve las métricas del MLP y de la fórmula lineal sobre el conjunto de prueba.
        """
        x = np.array(entradas, dtype=float)
        y = np.array(salidas, dtype=float)
        x_ent, x_pru, y_ent, y_pru = train_test_split(
            x, y, test_size=FRACCION_PRUEBA, random_state=self.semilla)

        x_esc = self.escalador_x.fit_transform(x_ent)
        y_esc = self.escalador_y.fit_transform(y_ent.reshape(-1, 1)).ravel()
        self.red.fit(x_esc, y_esc)
        self.entrenado = True

        self.metricas = self.comparar_con_formula(x_pru, y_pru)
        return self.metricas

    @staticmethod
    def _metricas(real, predicho):
        error = predicho - real
        mae = float(np.mean(np.abs(error)))
        rmse = float(np.sqrt(np.mean(error ** 2)))
        total = float(np.sum((real - np.mean(real)) ** 2))
        r2 = 1.0 - float(np.sum(error ** 2)) / total if total > 0 else 0.0
        return {"mae": mae, "rmse": rmse, "r2": r2}

    def comparar_con_formula(self, entradas, salidas):
        """Compara el MLP con la fórmula lineal de costos.py sobre los mismos datos."""
        x = np.array(entradas, dtype=float).reshape(-1, 3)
        y = np.array(salidas, dtype=float)
        pred_mlp = self.predecir_lote(x)
        pred_lineal = np.array([costos.costo_lineal(*fila) for fila in x])
        return {"mlp": self._metricas(y, pred_mlp),
                "lineal": self._metricas(y, pred_lineal),
                "n_prueba": int(len(y))}

    # ------------------------------------------------------------------
    # Predicción
    # ------------------------------------------------------------------
    def _verificar_entrenado(self):
        if not self.entrenado:
            raise RuntimeError("El modelo MLP no está entrenado ni cargado.")

    def predecir_lote(self, entradas):
        """Predice el costo de varias filas [distancia, dif_altitud, interferencia]."""
        self._verificar_entrenado()
        x = np.array(entradas, dtype=float).reshape(-1, 3)
        y_esc = self.red.predict(self.escalador_x.transform(x))
        return self.escalador_y.inverse_transform(y_esc.reshape(-1, 1)).ravel()

    def predecir_costo(self, distancia_km, dif_altitud_m, interferencia_prom):
        """Costo estimado de un enlace. Es el 'predictor' que recibe costos.calcular_costo."""
        return float(self.predecir_lote([[distancia_km, dif_altitud_m, interferencia_prom]])[0])

    def costo_sensores(self, a: NodoSensor, b: NodoSensor):
        """Costo de un enlace entre dos sensores; usa la fórmula lineal si el MLP falla."""
        return costos.calcular_costo(a, b, predictor=self.predecir_costo)

    def predecir_costos_enlaces(self, sensores: ListaEnlazada):
        """Costo MLP de los enlaces candidatos (351 para 27 sensores).

        Devuelve una ListaEnlazada de tuplas (id_u, id_v, costo).
        """
        return costos.calcular_costos_enlaces(sensores, predictor=self.predecir_costo)

    # ------------------------------------------------------------------
    # Persistencia (pickle)
    # ------------------------------------------------------------------
    def guardar(self, ruta=RUTA_MODELO):
        """Guarda el modelo entrenado. La carpeta de destino debe existir."""
        self._verificar_entrenado()
        contenido = {"semilla": self.semilla,
                     "escalador_x": self.escalador_x,
                     "escalador_y": self.escalador_y,
                     "red": self.red,
                     "metricas": self.metricas}
        with open(ruta, "wb") as archivo:
            pickle.dump(contenido, archivo)

    @classmethod
    def cargar(cls, ruta=RUTA_MODELO):
        """Carga un modelo guardado con guardar()."""
        with open(ruta, "rb") as archivo:
            contenido = pickle.load(archivo)
        modelo = cls(contenido["semilla"])
        modelo.escalador_x = contenido["escalador_x"]
        modelo.escalador_y = contenido["escalador_y"]
        modelo.red = contenido["red"]
        modelo.metricas = contenido["metricas"]
        modelo.entrenado = True
        return modelo


def cargar_o_entrenar(ruta_modelo=RUTA_MODELO, ruta_datos=RUTA_DEFECTO, forzar=False):
    """Devuelve un modelo listo para usar.

    1. Si existe el .pkl y se puede leer, lo carga.
    2. Si no, toma el CSV de entrenamiento (lo genera si no existe), entrena
       y guarda el modelo.
    """
    if not forzar and os.path.exists(ruta_modelo):
        try:
            return ModeloCostoMLP.cargar(ruta_modelo)
        except Exception:
            pass  # archivo dañado o incompatible: se vuelve a entrenar

    if not os.path.exists(ruta_datos):
        guardar_csv(generar_dataset(), ruta_datos)
    entradas, salidas = cargar_csv(ruta_datos)

    modelo = ModeloCostoMLP()
    modelo.entrenar(entradas, salidas)
    try:
        modelo.guardar(ruta_modelo)
    except OSError:
        pass  # sin carpeta de destino: el modelo sigue siendo utilizable en memoria
    return modelo


if __name__ == "__main__":
    modelo = cargar_o_entrenar(forzar=True)
    m = modelo.metricas
    print(f"Modelo MLP entrenado y guardado en {RUTA_MODELO} (semilla {SEMILLA})")
    print(f"Conjunto de prueba: {m['n_prueba']} enlaces")
    for nombre in ("mlp", "lineal"):
        r = m[nombre]
        print(f"  {nombre:7s} MAE = {r['mae']:.2f} | RMSE = {r['rmse']:.2f} | R2 = {r['r2']:.4f}")
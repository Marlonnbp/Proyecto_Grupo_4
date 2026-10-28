import os
import sys

# Asegurar que tanto el directorio raíz como codigo_fuente estén en sys.path
DIR_CODIGO = os.path.dirname(os.path.abspath(__file__))
DIR_RAIZ = os.path.dirname(DIR_CODIGO)
if DIR_RAIZ not in sys.path:
    sys.path.insert(0, DIR_RAIZ)
if DIR_CODIGO not in sys.path:
    sys.path.insert(0, DIR_CODIGO)

from codigo_fuente.carga_datos import cargar_datos_csv
from codigo_fuente.grafo import Grafo
from codigo_fuente.tabla_hash import TablaHash
from codigo_fuente.arista import Arista
from codigo_fuente.lista_enlazada import ListaEnlazada
from codigo_fuente.costos import (
    haversine,
    diferencia_altitud,
    interferencia_promedio,
    calcular_costo,
    calcular_costos_enlaces,
    distancia_sensores,
    costo_lineal,
)
from codigo_fuente.kruskal import kruskal
from codigo_fuente.verificador import verificar_arbol, verificar_red_operativa
from codigo_fuente.automata_sensor import (
    UMBRALES_POR_SUELO,
    umbral_de_suelo,
)
from codigo_fuente.simulacion_alerta import SimuladorAlerta, reconstruir_ruta

# Importación tolerante de la Red Neuronal MLP
try:
    from codigo_fuente.modelo_mlp import cargar_o_entrenar, ModeloCostoMLP
    MLP_DISPONIBLE = True
except (ImportError, ModuleNotFoundError):
    MLP_DISPONIBLE = False
    cargar_o_entrenar = None

# Rutas de datos
RUTA_CSV = os.path.join(DIR_RAIZ, "datos", "sensores_sismicos_peru.csv")
RUTA_MODELO = os.path.join(DIR_RAIZ, "datos", "modelo_mlp.pkl")
RUTA_DATOS_MLP = os.path.join(DIR_RAIZ, "datos", "entrenamiento_enlaces.csv")

NOMBRES_SUELO = {
    1: "Roca",
    2: "Arena",
    3: "Arcilla",
}


class SistemaSASPe:
    """Clase principal que administra el estado y las operaciones del simulador SASPe."""

    def __init__(self):
        self.grafo = Grafo()
        self.tabla_hash = TablaHash()
        self.modelo_mlp = None
        self.metodo_costo_usado = None  # "MLP" o "Fórmula lineal"
        self.costos_calculados = False
        self.arbol_mst = None
        self.enlaces_respaldo = ListaEnlazada()
        self.costo_mst = 0.0
        self.costo_respaldo = 0.0
        self.id_sede_central = "S01"  # Sede central por defecto (Lima)
        self.datos_cargados = False

    def cargar_sensores(self, silencioso=False):
        """1. Carga los sensores desde el archivo CSV."""
        if not os.path.exists(RUTA_CSV):
            if not silencioso:
                print(f"\n[ERROR] No se encontró el archivo: {RUTA_CSV}")
            return False

        try:
            self.grafo = Grafo()
            self.tabla_hash = TablaHash()
            cantidad = cargar_datos_csv(RUTA_CSV, self.grafo, self.tabla_hash)
            self.datos_cargados = True
            self.costos_calculados = False
            self.arbol_mst = None
            self.enlaces_respaldo = ListaEnlazada()

            # Verificar si la sede actual existe en los nuevos datos
            if not self.tabla_hash.contiene(self.id_sede_central):
                for sensor in self.grafo.vertices:
                    self.id_sede_central = sensor.id
                    break

            if not silencioso:
                print(f"\n[OK] Se cargaron {cantidad} estaciones sísmicas correctamente desde el CSV.")
            return True
        except Exception as e:
            if not silencioso:
                print(f"\n[ERROR] Error al procesar el archivo CSV: {e}")
            return False

    def calcular_costos_red(self, usar_mlp=True):
        """2. Calcula el costo de todos los enlaces usando MLP o Fórmula lineal."""
        if not self.datos_cargados:
            if not self.cargar_sensores(silencioso=True):
                return False

        predictor = None
        if usar_mlp:
            if not MLP_DISPONIBLE:
                print("\n[AVISO] Las librerías 'numpy' y 'scikit-learn' no están instaladas.")
                print("Se utilizará la fórmula lineal en su lugar.")
                self.metodo_costo_usado = "Fórmula lineal (Respaldo por falta de librerías)"
            else:
                try:
                    if self.modelo_mlp is None:
                        print("Inicializando modelo de Red Neuronal MLP...")
                        self.modelo_mlp = cargar_o_entrenar(RUTA_MODELO, RUTA_DATOS_MLP)
                    predictor = self.modelo_mlp.predecir_costo
                    self.metodo_costo_usado = "Red Neuronal MLP"
                except Exception as error:
                    print(f"\n[AVISO] No se pudo cargar el modelo MLP ({error}). Usando fórmula lineal.")
                    self.metodo_costo_usado = "Fórmula lineal (Fallback)"
        else:
            self.metodo_costo_usado = "Fórmula lineal ponderada"

        # Reiniciar las aristas del grafo para poblar con los nuevos costos
        enlaces = calcular_costos_enlaces(self.grafo.vertices, predictor=predictor)
        self.grafo.aristas = ListaEnlazada()
        for sensor in self.grafo.vertices:
            self.grafo.adyacencias[sensor.id] = ListaEnlazada()

        for id_u, id_v, costo in enlaces:
            self.grafo.agregar_arista(id_u, id_v, costo)

        self.costos_calculados = True
        self.arbol_mst = None
        self.enlaces_respaldo = ListaEnlazada()
        return True

    def construir_red(self, cantidad_respaldos=3):
        """3. Construye el árbol de Kruskal y añade enlaces de respaldo."""
        if not self.costos_calculados:
            self.calcular_costos_red(usar_mlp=True)

        # 1. Ejecutar Kruskal para el Árbol de Expansión Mínima
        self.arbol_mst, self.costo_mst = kruskal(self.grafo)

        # 2. Identificar aristas que no están en el árbol como candidatas a respaldo
        aristas_arbol = set()
        for a in self.arbol_mst:
            menor, mayor = sorted((a.origen, a.destino))
            aristas_arbol.add((menor, mayor))

        candidatas_respaldo = []
        for a in self.grafo.aristas:
            menor, mayor = sorted((a.origen, a.destino))
            if (menor, mayor) not in aristas_arbol:
                candidatas_respaldo.append(a)

        # Ordenar candidatas por menor costo
        candidatas_respaldo.sort()

        self.enlaces_respaldo = ListaEnlazada()
        self.costo_respaldo = 0.0
        for arista in candidatas_respaldo[:cantidad_respaldos]:
            self.enlaces_respaldo.agregar_al_final(arista)
            self.costo_respaldo += arista.costo

        return self.arbol_mst, self.enlaces_respaldo

    def obtener_red_operativa(self):
        """Devuelve la lista de todas las aristas (árbol base + enlaces de respaldo)."""
        if self.arbol_mst is None:
            self.construir_red()
        todas = ListaEnlazada()
        for a in self.arbol_mst:
            todas.agregar_al_final(a)
        for a in self.enlaces_respaldo:
            todas.agregar_al_final(a)
        return todas

    def obtener_ruta_red(self, origen, destino):
        """Calcula la ruta y costo entre dos sensores en la red operativa."""
        red = self.obtener_red_operativa()

        ady = {}
        for sensor in self.grafo.vertices:
            ady[sensor.id] = []

        for arista in red:
            ady[arista.origen].append((arista.destino, arista.costo))
            ady[arista.destino].append((arista.origen, arista.costo))

        # BFS para encontrar camino y registrar predecesores
        cola = [origen]
        visitados = {origen}
        predecesores = {origen: None}
        costos = {origen: 0.0}

        encontrado = False
        while cola:
            actual = cola.pop(0)
            if actual == destino:
                encontrado = True
                break
            for vecino, costo in ady.get(actual, []):
                if vecino not in visitados:
                    visitados.add(vecino)
                    predecesores[vecino] = actual
                    costos[vecino] = costos[actual] + costo
                    cola.append(vecino)

        if not encontrado:
            return None

        ruta = reconstruir_ruta(predecesores, origen, destino)
        if ruta is None:
            return None
        return ruta, costos[destino]


# ----------------------------------------------------------------------
# Funciones de Soporte de Interfaz de Usuario
# ----------------------------------------------------------------------

def pausar():
    try:
        input("\nPresione [ENTER] para volver al menú...")
    except (EOFError, KeyboardInterrupt):
        pass


def opcion_1_cargar_sensores(sistema: SistemaSASPe):
    print("\n" + "=" * 70)
    print(" 1. CARGAR SENSORES DESDE EL CSV")
    print("=" * 70)

    if not sistema.cargar_sensores():
        pausar()
        return

    total = sistema.tabla_hash.obtener_tamano()
    print(f"\nSe encontraron {total} estaciones registradas:")
    print("-" * 70)
    print(f"{'ID':<6} {'Ciudad':<15} {'Latitud':<10} {'Longitud':<10} {'Alt(m)':<8} {'Suelo':<10} {'RF':<4}")
    print("-" * 70)

    for sensor in sistema.grafo.vertices:
        suelo_desc = NOMBRES_SUELO.get(sensor.tipo_suelo, str(sensor.tipo_suelo))
        print(f"{sensor.id:<6} {sensor.ciudad:<15} {sensor.latitud:<10.4f} {sensor.longitud:<10.4f} "
              f"{sensor.altitud:<8.0f} {suelo_desc:<10} {sensor.interferencia_rf:<4}")
    print("-" * 70)
    pausar()


def opcion_2_calcular_costos(sistema: SistemaSASPe):
    print("\n" + "=" * 70)
    print(" 2. CALCULAR EL COSTO DE LOS ENLACES (MLP O FÓRMULA)")
    print("=" * 70)

    if not sistema.datos_cargados:
        sistema.cargar_sensores(silencioso=True)

    print("\nSeleccione el método de cálculo para los enlaces:")
    print("  1. Red Neuronal MLP (Regresión con machine learning)")
    print("  2. Fórmula lineal ponderada (Haversine + Altitud + Interferencia RF)")
    sub_opcion = input("Opción [1-2, por defecto 1]: ").strip()

    usar_mlp = (sub_opcion != "2")

    print("\nCalculando costos de todos los enlaces candidatos...")
    sistema.calcular_costos_red(usar_mlp=usar_mlp)

    total_aristas = sistema.grafo.cantidad_aristas()
    costos = [a.costo for a in sistema.grafo.aristas]

    print("\n" + "-" * 55)
    print(" RESUMEN DEL CÁLCULO DE COSTOS")
    print("-" * 55)
    print(f" Método aplicado           : {sistema.metodo_costo_usado}")
    print(f" Enlaces calculados        : {total_aristas}")
    if costos:
        print(f" Costo mínimo de enlace    : {min(costos):.2f}")
        print(f" Costo máximo de enlace    : {max(costos):.2f}")
        print(f" Costo promedio por enlace : {sum(costos)/len(costos):.2f}")
    print("-" * 55)

    consultar = input("\n¿Desea consultar el costo específico entre dos sensores? (s/n): ").strip().lower()
    if consultar == "s":
        id_a = input("ID del primer sensor (ej. S01): ").strip().upper()
        id_b = input("ID del segundo sensor (ej. S05): ").strip().upper()
        sensor_a = sistema.tabla_hash.buscar(id_a)
        sensor_b = sistema.tabla_hash.buscar(id_b)

        if not sensor_a or not sensor_b:
            print("\n[!] Uno o ambos IDs ingresados no existen.")
        elif id_a == id_b:
            print("\n[!] Debe ingresar dos sensores distintos.")
        else:
            dist = distancia_sensores(sensor_a, sensor_b)
            alt = diferencia_altitud(sensor_a, sensor_b)
            rf = interferencia_promedio(sensor_a, sensor_b)
            costo = calcular_costo(
                sensor_a,
                sensor_b,
                predictor=sistema.modelo_mlp.predecir_costo if (usar_mlp and sistema.modelo_mlp) else None
            )
            print("\n" + "-" * 50)
            print(f" Enlace: {sensor_a.ciudad} ({id_a}) <---> {sensor_b.ciudad} ({id_b})")
            print(f" Distancia Haversine : {dist:.2f} km")
            print(f" Desnivel altitud    : {alt:.1f} m")
            print(f" Interferencia RF    : {rf:.2f} / 10")
            print(f" Costo estimado      : {costo:.2f}")
            print("-" * 50)

    pausar()


def opcion_3_construir_red(sistema: SistemaSASPe):
    print("\n" + "=" * 70)
    print(" 3. CONSTRUIR LA RED: KRUSKAL Y ENLACES DE RESPALDO")
    print("=" * 70)

    if not sistema.datos_cargados:
        sistema.cargar_sensores(silencioso=True)

    print("\nParámetros de diseño de la red:")
    resp_input = input("¿Cuántos enlaces de respaldo desea agregar? [Por defecto 3]: ").strip()
    try:
        n_resp = int(resp_input) if resp_input else 3
        if n_resp < 0:
            n_resp = 3
    except ValueError:
        n_resp = 3

    print(f"\nEjecutando algoritmo de Kruskal y seleccionando {n_resp} enlaces de respaldo...")
    arbol, respaldos = sistema.construir_red(cantidad_respaldos=n_resp)

    print("\n" + "-" * 60)
    print(" ESTRUCTURA DE LA RED CONSTRUIDA")
    print("-" * 60)
    print(f" Vértices conectados (Estaciones)  : {sistema.grafo.cantidad_vertices()}")
    print(f" Enlaces principales (Árbol MST)   : {arbol.obtener_tamano()} aristas")
    print(f" Costo del Árbol de Expansión (MST): {sistema.costo_mst:.2f}")
    print(f" Enlaces de respaldo incorporados : {respaldos.obtener_tamano()} aristas")
    print(f" Costo adicional por respaldos    : {sistema.costo_respaldo:.2f}")
    print(f" Total de enlaces en red operativa : {arbol.obtener_tamano() + respaldos.obtener_tamano()} aristas")
    print(f" Costo Total de la Red Operativa  : {sistema.costo_mst + sistema.costo_respaldo:.2f}")
    print("-" * 60)

    pausar()


def opcion_4_verificar_y_consultar_red(sistema: SistemaSASPe):
    print("\n" + "=" * 70)
    print(" 4. VERIFICAR LA RED Y CONSULTAR SUS ENLACES")
    print("=" * 70)

    if sistema.arbol_mst is None:
        print("\nConstruyendo la red previamente...")
        sistema.construir_red()

    # 1. Verificación algorítmica con DFS
    verif_arbol = verificar_arbol(sistema.grafo, sistema.arbol_mst)
    red_operativa = sistema.obtener_red_operativa()
    verif_operativa = verificar_red_operativa(sistema.grafo, red_operativa)

    print("\n" + "-" * 60)
    print(" REPORTE DE VERIFICACIÓN DE TOPOLOGÍA (DFS)")
    print("-" * 60)
    print(f" Árbol Base - Aristas esperadas    : {verif_arbol['aristas_esperadas']}")
    print(f" Árbol Base - Aristas obtenidas    : {verif_arbol['aristas_obtenidas']}")
    print(f" Árbol Base - ¿Es conexo?          : {'Sí' if verif_arbol['conexo'] else 'No'}")
    print(f" Árbol Base - ¿Libre de ciclos?    : {'Sí' if verif_arbol['sin_ciclos'] else 'No'}")
    print(f" Árbol Base - Estado formal        : {'VÁLIDO' if verif_arbol['valido'] else 'INVÁLIDO'}")
    print("-" * 60)
    print(f" Red Operativa - Total de enlaces  : {verif_operativa['aristas']}")
    print(f" Red Operativa - ¿Es conexa?       : {'Sí' if verif_operativa['conexa'] else 'No'}")
    print(f" Red Operativa - Costo total       : {verif_operativa['costo_total']:.2f}")
    print("-" * 60)

    # 2. Submenú de consulta de enlaces
    print("\nOpciones de consulta:")
    print("  a. Ver todos los enlaces del Árbol de Expansión Mínima (MST)")
    print("  b. Ver los enlaces de respaldo")
    print("  c. Consultar enlaces conectados a una estación específica")
    print("  d. Omitir y continuar")
    sub = input("Seleccione una opción [a/b/c/d]: ").strip().lower()

    if sub == "a":
        print("\n--- ENLACES DEL ÁRBOL BASE (MST) ---")
        print(f"{'Origen':<8} {'Destino':<8} {'Costo':<10} {'Tramo':<30}")
        print("-" * 60)
        for a in sistema.arbol_mst:
            s_u = sistema.tabla_hash.buscar(a.origen)
            s_v = sistema.tabla_hash.buscar(a.destino)
            n_u = s_u.ciudad if s_u else a.origen
            n_v = s_v.ciudad if s_v else a.destino
            print(f"{a.origen:<8} {a.destino:<8} {a.costo:<10.2f} {n_u} - {n_v}")
    elif sub == "b":
        print("\n--- ENLACES DE RESPALDO SELECCIONADOS ---")
        if sistema.enlaces_respaldo.obtener_tamano() == 0:
            print("No hay enlaces de respaldo registrados.")
        else:
            print(f"{'Origen':<8} {'Destino':<8} {'Costo':<10} {'Tramo':<30}")
            print("-" * 60)
            for a in sistema.enlaces_respaldo:
                s_u = sistema.tabla_hash.buscar(a.origen)
                s_v = sistema.tabla_hash.buscar(a.destino)
                n_u = s_u.ciudad if s_u else a.origen
                n_v = s_v.ciudad if s_v else a.destino
                print(f"{a.origen:<8} {a.destino:<8} {a.costo:<10.2f} {n_u} - {n_v}")
    elif sub == "c":
        id_busqueda = input("\nIngrese el ID de la estación a consultar (ej. S01): ").strip().upper()
        if not sistema.tabla_hash.contiene(id_busqueda):
            print(f"[!] La estación '{id_busqueda}' no existe.")
        else:
            s_act = sistema.tabla_hash.buscar(id_busqueda)
            print(f"\nEnlaces directos conectados a {s_act.ciudad} ({id_busqueda}):")
            print("-" * 55)
            encontrados = 0
            for a in red_operativa:
                otro_id = None
                if a.origen == id_busqueda:
                    otro_id = a.destino
                elif a.destino == id_busqueda:
                    otro_id = a.origen

                if otro_id:
                    s_vecino = sistema.tabla_hash.buscar(otro_id)
                    n_vecino = s_vecino.ciudad if s_vecino else otro_id
                    print(f" <---> Conectado con {otro_id} ({n_vecino}) | Costo: {a.costo:.2f}")
                    encontrados += 1
            if encontrados == 0:
                print("No se encontraron enlaces conectados a esta estación.")

    pausar()


def opcion_5_elegir_sede_central(sistema: SistemaSASPe):
    print("\n" + "=" * 70)
    print(" 5. ELEGIR LA SEDE CENTRAL")
    print("=" * 70)

    if not sistema.datos_cargados:
        sistema.cargar_sensores(silencioso=True)

    sede_actual = sistema.tabla_hash.buscar(sistema.id_sede_central)
    nombre_actual = sede_actual.ciudad if sede_actual else "Desconocida"

    print(f"\nSede central actual: {sistema.id_sede_central} ({nombre_actual})")
    print("La sede central es la estación de monitoreo destino de todas las alertas sísmicas.\n")

    nuevo_id = input("Ingrese el ID de la nueva sede central (o presione ENTER para mantener): ").strip().upper()

    if not nuevo_id:
        print("\nSe mantiene la sede central actual.")
    elif not sistema.tabla_hash.contiene(nuevo_id):
        print(f"\n[!] Error: El sensor '{nuevo_id}' no existe en el sistema.")
    else:
        sistema.id_sede_central = nuevo_id
        nueva_sede = sistema.tabla_hash.buscar(nuevo_id)
        print(f"\n[OK] Sede central actualizada con éxito a: {nuevo_id} ({nueva_sede.ciudad})")

    pausar()


def opcion_6_simular_evento_sismico(sistema: SistemaSASPe):
    print("\n" + "=" * 70)
    print(" 6. SIMULAR UN EVENTO SÍSMICO Y VER LA RUTA Y EL REPORTE")
    print("=" * 70)

    if not sistema.datos_cargados:
        sistema.cargar_sensores(silencioso=True)
    if sistema.arbol_mst is None:
        sistema.construir_red()

    sede_actual = sistema.tabla_hash.buscar(sistema.id_sede_central)
    nombre_sede = sede_actual.ciudad if sede_actual else sistema.id_sede_central
    print(f"\nSede central receptora configurada: {sistema.id_sede_central} ({nombre_sede})")

    id_epicentro = input("Ingrese ID del sensor epicentro (ejemplo: S05): ").strip().upper()
    sensor_origen = sistema.tabla_hash.buscar(id_epicentro)

    if not sensor_origen:
        print(f"\n[!] El sensor epicentro '{id_epicentro}' no existe.")
        pausar()
        return

    try:
        mag_str = input("Ingrese la magnitud del evento sísmico (ejemplo: 6.8): ").strip()
        magnitud = float(mag_str)
        if magnitud < 0:
            raise ValueError()
    except ValueError:
        print("\n[!] Magnitud inválida. Debe ser un número positivo.")
        pausar()
        return

    # Preparar el simulador de alertas con la función de ruta de la red
    pares_sensores = [(s.id, s.tipo_suelo) for s in sistema.grafo.vertices]
    simulador = SimuladorAlerta(pares_sensores, sistema.obtener_ruta_red)

    print("\nProcesando evento sísmico en el autómata y evaluando propagación...")
    reporte = simulador.simular_evento(id_epicentro, magnitud, sistema.id_sede_central)

    print("\n" + "=" * 55)
    print(str(reporte))
    print("=" * 55)

    if reporte.propagada and reporte.ruta:
        print("\nDesglose de la ruta de propagación:")
        for idx, id_paso in enumerate(reporte.ruta):
            s_paso = sistema.tabla_hash.buscar(id_paso)
            nom = s_paso.ciudad if s_paso else id_paso
            if idx == 0:
                print(f" [Inicio Epicentro] -> {id_paso} ({nom})")
            elif idx == len(reporte.ruta) - 1:
                print(f" [Destino Central]  -> {id_paso} ({nom})")
            else:
                print(f" [Salto {idx:02d}]          -> {id_paso} ({nom})")

    pausar()


# ----------------------------------------------------------------------
# Menú Principal
# ----------------------------------------------------------------------

def mostrar_menu(sede_actual):
    print("\n" + "=" * 65)
    print("        SISTEMA DE ALERTA SÍSMICA DEL PERÚ (SASPe)")
    print(f"        Sede Central Actual: {sede_actual}")
    print("=" * 65)
    print(" 1. Cargar sensores desde el CSV")
    print(" 2. Calcular el costo de los enlaces (MLP o fórmula)")
    print(" 3. Construir la red: Kruskal y enlaces de respaldo")
    print(" 4. Verificar la red y consultar sus enlaces")
    print(" 5. Elegir la sede central")
    print(" 6. Simular un evento sísmico y ver la ruta y el reporte")
    print(" 7. Salir")
    print("=" * 65)


def main():
    sistema = SistemaSASPe()
    # Carga inicial silenciosa para que los datos estén disponibles de inmediato
    sistema.cargar_sensores(silencioso=True)

    while True:
        sede_sensor = sistema.tabla_hash.buscar(sistema.id_sede_central)
        nombre_sede = f"{sistema.id_sede_central} ({sede_sensor.ciudad})" if sede_sensor else sistema.id_sede_central
        mostrar_menu(nombre_sede)

        try:
            opcion = input("Seleccione una opción [1-7]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nSaliendo del sistema...")
            break

        if opcion == "1":
            opcion_1_cargar_sensores(sistema)
        elif opcion == "2":
            opcion_2_calcular_costos(sistema)
        elif opcion == "3":
            opcion_3_construir_red(sistema)
        elif opcion == "4":
            opcion_4_verificar_y_consultar_red(sistema)
        elif opcion == "5":
            opcion_5_elegir_sede_central(sistema)
        elif opcion == "6":
            opcion_6_simular_evento_sismico(sistema)
        elif opcion == "7":
            print("\n¡Gracias por utilizar el sistema SASPe! Hasta pronto.\n")
            break
        else:
            print("\n[!] Opción no válida. Por favor elija un número del 1 al 7.")
            pausar()


if __name__ == "__main__":
    main()

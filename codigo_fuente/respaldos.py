from codigo_fuente.recorridos import bfs_saltos

def seleccionar_respaldos(grafo_base, aristas_descartadas, R=8):
    respaldos_seleccionados = []
    contador_respaldos_sensor = {}  # Lleva el control del límite de 2 por sensor
    
    # Ordenar las aristas descartadas de menor a mayor costo
    aristas_ordenadas = sorted(aristas_descartadas, key=lambda a: a.costo)
    
    for arista in aristas_ordenadas:
        if len(respaldos_seleccionados) >= R:
            break
            
        u, v = arista.origen, arista.destino
        
        # Calculamos los saltos en el árbol base usando el BFS del grafo adaptado
        distancias_desde_u = bfs_saltos(grafo_base, u)
        saltos = distancias_desde_u.get(v, float('inf'))
        
        # (a) Excluir los que unen sensores a menos de 3 saltos en el árbol
        if saltos < 3:
            continue
            
        # Verificar la restricción: no más de 2 respaldos en un mismo sensor
        resp_u = contador_respaldos_sensor.get(u, 0)
        resp_v = contador_respaldos_sensor.get(v, 0)
        
        if resp_u < 2 and resp_v < 2:
            respaldos_seleccionados.append(arista)
            contador_respaldos_sensor[u] = resp_u + 1
            contador_respaldos_sensor[v] = resp_v + 1
            
    return respaldos_seleccionados
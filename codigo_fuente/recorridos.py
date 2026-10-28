from codigo_fuente.cola import Cola  # Tu cola propia

def bfs_saltos(grafo, origen_id):
    distancias = {origen_id: 0}
    visitados = {origen_id}
    
    cola = Cola()
    cola.encolar(origen_id)
    
    while not cola.esta_vacia():
        actual = cola.desencolar()
        distancia_actual = distancias[actual]
        
        # Obtenemos la ListaEnlazada de Aristas adyacentes al nodo actual
        aristas_adyacentes = grafo.obtener_vecinos(actual)
        
        for arista in aristas_adyacentes:
            vecino = arista.destino if arista.origen == actual else arista.origen
            
            if vecino not in visitados:
                visitados.add(vecino)
                distancias[vecino] = distancia_actual + 1
                cola.encolar(vecino)
                
    return distancias


def bfs_camino(grafo, origen_id, destino_id):
    if origen_id not in grafo.adyacencias or destino_id not in grafo.adyacencias:
        return []
        
    visitados = {origen_id}
    predecesores = {origen_id: None}
    
    cola = Cola()
    cola.encolar(origen_id)
    
    encontrado = False
    while not cola.esta_vacia():
        actual = cola.desencolar()
        
        if actual == destino_id:
            encontrado = True
            break
            
        aristas_adyacentes = grafo.obtener_vecinos(actual)
        for arista in aristas_adyacentes:
            vecino = arista.destino if arista.origen == actual else arista.origen
            
            if vecino not in visitados:
                visitados.add(visitado) 
                visitados.add(vecino)
                predecesores[vecino] = actual
                cola.encolar(vecino)
                
    if not encontrado:
        return []
        
    # Reconstrucción de la ruta
    camino = []
    curr = destino_id
    while curr is not None:
        camino.append(curr)
        curr = predecesores[curr]
        
    camino.reverse()
    return camino
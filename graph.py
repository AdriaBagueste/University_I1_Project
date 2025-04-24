from node import *
from segment import *
import matplotlib.pyplot as plt 
import numpy as np
import math
from path import *

class Graph:
    def __init__ (self):
        self.node = []
        self.segment = []

def AddNode (g, n):
    for node in g.node:
        if node.name == n.name:
            return False
    g.node.append(n)
    return True

def DetectEntry (entryNode):
    text = entryNode.replace(',', ' ')
    partes = text.split(' ')
    if len(partes) == 3:
        if partes[1].isdigit():
            name = partes[0]
            x = float(partes[1])
            y = float(partes[2])
            d = Node(name, x, y)
        elif partes[1].isalpha():
            d = [partes[0], partes[1], partes[2]]
    elif len(partes) == 2:
        d = [partes[0], partes[1]]
    return d

def DeleteSegment (g, s):
    newsegments = []
    for d in g.segment:
        if d.name != s:
            newsegments.append(d)
    g.segment = newsegments
    return g

def DeleteNode (g, n):
    newNodes = []
    for d in g.node:
        if d.name != n:
            newNodes.append(d)
    g.node = newNodes
    newsegments = []
    for d in g.segment:
        if d.origin.name != n and d.destination.name != n:
            newsegments.append(d)
    g.segment = newsegments
    return g

def AddSegment (g, segmentName, nameOriginNode, nameDestinationNode):
    nO = False
    nD = False
    for node in g.node:
        if node.name == nameOriginNode:
            nO = True
            n1 = node
        elif node.name == nameDestinationNode:
            nD = True
            n2 = node
    if nO == True and nD == True:
        n1.neighbors.append(n2)
        s = Segment (segmentName, n1, n2)
        g.segment.append(s)
        return True
    else:
        return False
    
def GetClosest (g, x, y):
    point = Node ('p', x, y)
    closest = g.node[0]
    min_dist = Distance(closest, point)
    for n in g.node[1:]:
        d = Distance(n, point)
        if d < min_dist:
            closest = n
            min_dist = d
    return closest

def Plot(g):
    for n in g.node:
        plt.plot(n.x ,n.y, 'o', color='red', markersize=3)
        plt.text(n.x, n.y, f'{n.name}', fontsize=8, color='black')
    for s in g.segment:
        plt.arrow(s.origin.x, s.origin.y, s.destination.x - s.origin.x, s.destination.y - s.origin.y,
                   head_width=0.2, head_length=0.3, fc='blue', ec='blue', linewidth=0.5, length_includes_head=True)
        midx = (s.origin.x + s.destination.x) / 2
        midy = (s.origin.y + s.destination.y) / 2
        plt.text(midx, midy, f'{s.cost} km', fontsize=7, weight='bold')
    plt.grid(color='gray', linestyle='dashed', linewidth=0.5)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.show()

def PlotNode(g, nameOrigin):
    found = False
    origin = None

    for n in g.node:
        if n.name == nameOrigin:
            origin = n
            plt.plot(n.x, n.y, 'o', color='blue', markersize=5)
            plt.text(n.x, n.y, f'{n.name}', fontsize=8, color='black')
            found = True
            break
    if found == False:
        return False
    
    for s in g.segment:
        if s.origin.name == nameOrigin:
            plt.plot(s.destination.x, s.destination.y, 'o', color = 'green', markersize = 3)
            plt.text(s.destination.x, s.destination.y, f'{s.destination.name}', fontsize=8, color='black')
            plt.arrow(s.origin.x, s.origin.y, s.destination.x - s.origin.x, s.destination.y - s.origin.y, head_width=0.2, head_length=0.3, fc='red', ec='red', linewidth=0.5, length_includes_head=True)
            midx = (s.origin.x + s.destination.x) / 2
            midy = (s.origin.y + s.destination.y) / 2
            plt.text(midx, midy, f'{s.cost} km', fontsize=7, weight='bold')
    
    for n in g.node:
        for neighbor in origin.neighbors:
            if n != neighbor:
                plt.plot(n.x, n.y, 'o', color='gray', markersize=3)
                plt.text(n.x, n.y, f'{n.name}', fontsize=8, color='black')

    plt.grid(color='grey', linestyle='dashed', linewidth=0.5)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.show()

def LoadFile (fileName):
    X = open(fileName, 'r')
    lines = X.readlines()
    g = Graph()
    type = 'x'
    for line in lines:
        line = line.strip()
        if line == 'Nodes:':
            type = 'n'
            continue
        elif line == 'Segments:':
            type = 's'
            continue
        if type == 'n':
            trozo = line.split(' ')
            if len(trozo) == 3:
                name = trozo[0]
                x = float(trozo[1])
                y = float(trozo[2])
                n = Node(name, x, y)
                AddNode(g, n)
        elif type == 's':
            trozo = line.split(' ')
            if len(trozo) == 3:
                name = trozo[0]
                origin = trozo[1]
                destination = trozo[2]
                AddSegment(g, name, origin, destination)
        else:
            break
    return g

def PlotFile(fileName):
    g = LoadFile(fileName)
    Plot(g)

def NewGraph(g):
    g.node.clear()
    g.segment.clear()
    return g

def SaveGraph(g):
    X = open('Graph.txt', 'w')
    X.write('Nodes:\n')
    for n in g.node:
        X.write(f'{n.name} {n.x} {n.y}\n')
    X.write('Segments:\n')
    for s in g.segment:
        X.write(f'{s.name} {s.origin.name} {s.destination.name}\n')
    print('Graph saved successfully.')

def Reachability(g, startNodeName):
    start_node = None
    for n in g.node:
        if n.name == startNodeName:
            start_node = n
            break
    print(f'Start node: {start_node.name}')
    lista = [start_node]
    i = 0
    
    while i < len(lista):
        actual = lista[i]
        for vecino in actual.neighbors:
            # aqui miro si el vecino ya esta en la lista esa
            finalizado = False
            for nodo in lista:
                if nodo == vecino:
                    finalizado = True
                    break
            
            if not finalizado:
                for s in g.segment:
                    if s.origin == actual and s.destination == vecino:
                        lista.append(vecino)
                        print(f'Adding segment: {s.name}')
                        break
        i += 1
    return lista

def PlotReachability(g, lista):
    origin = lista[0]

    for n in g.node:
        if n == origin:
            plt.plot(origin.x, origin.y, 'o', color='blue', markersize=5)
        elif n in lista and n != origin:
            plt.plot(n.x, n.y, 'o', color='red', markersize=5)
        else:
            plt.plot(n.x, n.y, 'o', color='gray', markersize=3)
        plt.text(n.x, n.y, f'{n.name}', fontsize=8, color='black')
    
    for s in g.segment:
        if s.origin in lista and s.destination in lista:
            plt.arrow(s.origin.x, s.origin.y, s.destination.x - s.origin.x, s.destination.y - s.origin.y, 
                      head_width=0.2, head_length=0.3, fc='red', ec='red', linewidth=0.5, length_includes_head=True)
        else:
            plt.arrow(s.origin.x, s.origin.y, s.destination.x - s.origin.x, s.destination.y - s.origin.y, 
                      head_width=0.2, head_length=0.3, fc='gray', ec='gray', linewidth=0.5, length_includes_head=True)
        midx = (s.origin.x + s.destination.x) / 2
        midy = (s.origin.y + s.destination.y) / 2
        plt.text(midx, midy, f'{s.cost} km', fontsize=7, weight='bold')
    plt.grid(color='grey', linestyle='dashed', linewidth=0.5)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.show()

def FindShortestPath (g, originName, destinationName):
    alcanzables = Reachability(g, originName)
    destination = None
    origin = None
    for n in g.node:
        if n.name == destinationName:
            destination = n
        if n.name == originName:
            origin = n
        if destination and origin:
            break
    if destination not in alcanzables:
        return None
    
    caminos_posibles = [[origin]]
    costes_acumulados = [0.0]
    while caminos_posibles: #mientras haya caminos posibles dentro de la lista esa...
        menor_coste = costes_acumulados[0]
        index_menor = 0
        i = 0
        while i < len(caminos_posibles): #aqui miro cual es el camino mas corto
            if costes_acumulados[i] < menor_coste:
                menor_coste = costes_acumulados[i]
                index_menor = i
            i += 1
        
        camino_actual = caminos_posibles.pop(index_menor)
        coste_actual = costes_acumulados.pop(index_menor)
        ultimo_nodo = camino_actual[-1]

        if ultimo_nodo == destination: #aqui es donde acaba ya toda la funcion
            path_resultado = Path(origin)
            for node in camino_actual[1:]:
                last = path_resultado.nodes[-1]
                path_resultado.cost += round(Distance(last, node), 2)
                path_resultado.nodes.append(node)
            return path_resultado
        
        for vecino in ultimo_nodo.neighbors: #aqui mira los vecinos del ultimo nodo
            vecino_en_camino = False
            for node in camino_actual: #esto es para ver si el vecino ya esta en la lista de caminos o no y no volver a añadirlo
                if node == vecino:
                    vecino_en_camino = True
                    break
            
            if not vecino_en_camino: #aqui es donde añado los nodos y el cost nuevos para volver al bucle
                coste_segmento = 0
                for segment in g.segment:
                    if segment.origin == ultimo_nodo and segment.destination == vecino:
                        coste_segmento = segment.cost
                        break
                if coste_segmento > 0:
                    nuevo_camino = camino_actual.copy() #con el .copy() hago una copia del camino actual y no lo modifico
                    nuevo_camino.append(vecino)
                    caminos_posibles.append(nuevo_camino)
                    costes_acumulados.append(coste_actual + coste_segmento)
    return None
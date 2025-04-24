from path import *
from graph import *

def CreateGraph_1 ():
    G = Graph()
    AddNode(G, Node("A",1,20))
    AddNode(G, Node("B",8,17))
    AddNode(G, Node("C",15,20))
    AddNode(G, Node("D",18,15))
    AddNode(G, Node("E",2,4))
    AddNode(G, Node("F",6,5))
    AddNode(G, Node("G",12,12))
    AddNode(G, Node("H",10,3))
    AddNode(G, Node("I",19,1))
    AddNode(G, Node("J",13,5))
    AddNode(G, Node("K",3,15))
    AddNode(G, Node("L",4,10))
    AddSegment(G, "AE","A","E")
    AddSegment(G, "AK","A","K")
    AddSegment(G, "BC","B","C")
    AddSegment(G, "BK","B","K")
    AddSegment(G, "CG","C","G")
    AddSegment(G, "DG","D","G")
    AddSegment(G, "DH","D","H")
    AddSegment(G, "DI","D","I")
    AddSegment(G, "EF","E","F")
    AddSegment(G, "FL","F","L")
    AddSegment(G, "GB","G","B")
    AddSegment(G, "GH","G","H")
    AddSegment(G, "ID","I","D")
    AddSegment(G, "IJ","I","J")
    AddSegment(G, "JI","J","I")
    AddSegment(G, "KA","K","A")
    AddSegment(G, "KL","K","L")
    AddSegment(G, "LK","L","K")
    AddSegment(G, "LF","L","F")
    return G
G = CreateGraph_1 ()

n1 = G.node[0]  # Nodo A
n2 = G.node[10]  # Nodo K
n3 = G.node[2]  # Nodo C

path = Path(n1)
print("Path creado:", [n.name for n in path.nodes], "Costo:", path.cost)

AddNodeToPath(path, n2)
print("Path después de añadir nodo K:", [n.name for n in path.nodes], "Costo:", path.cost)

print("¿Contiene A?", ContainsNode(path, n1))
print("¿Contiene K?", ContainsNode(path, n2))
print("¿Contiene C?", ContainsNode(path, n3))

print("Costo hasta A:", CostToNode(path, n1))
print("Costo hasta K:", CostToNode(path, n2))
print("Costo hasta C:", CostToNode(path, n3))

print("Mostrando path:")
PlotPath(G, path)
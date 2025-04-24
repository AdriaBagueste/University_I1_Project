import math

class Node:
    def __init__ (self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.neighbors = [] #Node B will be considered a neighbor of A if there is a segment with origin in A and destination in B

def AddNeighbor (n1, n2):
    add = True
    for node in n1.neighbors:
        if node == n2:
            add = False
            break
    if add == True:
        n1.neighbors.append(n2)
    return add
        
def Distance (n1, n2):
    x = (n1.x) - (n2.x)
    y = (n1.y) - (n2.y)
    dist = math.sqrt((x**2) + (y**2))
    return dist
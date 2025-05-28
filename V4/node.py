class Node:

    def __init__(self, name : str, coordinate_x : float, coordinate_y : float):
        self.name : str = name
        self.coordinate_x : float = coordinate_x
        self.coordinate_y : float = coordinate_y
        self.list_of_neighbors : list = []

def AddNeighbor(n1 : Node, n2 : Node):
    Found = False

    for i in n1.list_of_neighbors:
        if i.name == n2.name:
            Found = True
    
    if Found:
        return False
    elif not Found:
        n1.list_of_neighbors.append(n2)
        return True
    
def Distance(n1 : Node, n2 : Node):
    from math import sqrt

    Distance = sqrt((n1.coordinate_x - n2.coordinate_x)**2 + (n1.coordinate_y - n2.coordinate_y)**2)

    return Distance


        

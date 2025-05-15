from node import *
from segment import *

class Graph:

    def __init__(self):
        self.list_of_nodes : list = []
        self.list_of_segments : list = []

def GetNodeByName(G: Graph, name: str):
    for node in G.list_of_nodes:
        if node.name == name:
            return node
    return None 

def AddNode(G : Graph, n : Node):
    Found = False

    for i in G.list_of_nodes:
        if i == n:
            Found = True

    if Found:
        return False
    elif not Found:
        G.list_of_nodes.append(n)
        return True
    
def AddSegment(G : Graph, name_segment, nameOriginNode : str, nameDestinationNode : str):
    
    origin_node : Node = GetNodeByName(G, nameOriginNode)
    destination_node : Node = GetNodeByName(G, nameDestinationNode)

    s = Segment(name_segment, origin_node, destination_node)

    G.list_of_segments.append(s)

    origin_node.list_of_neighbors.append(destination_node)

    return True
    
def GetClosest(G : Graph, x : float, y : float):
    from math import sqrt

    Distances  = []

    for i in G.list_of_nodes:
        Distances.append(sqrt((i.coordinate_x - x)**2 + (i.coordinate_y - y)**2))

    return G.list_of_nodes[Distances.index(min(Distances))]

def Plot(G : Graph):
    import matplotlib.pyplot as plt

    plt.clf()
    fig = plt.figure()

    for i in G.list_of_segments:
        line_x : list = [i.origin_node.coordinate_x, i.destination_node.coordinate_x]
        line_y :list = [i.origin_node.coordinate_y, i.destination_node.coordinate_y]

        plt.plot(line_x, line_y, color= 'blue')

    for i in G.list_of_nodes:
        plt.scatter(i.coordinate_x, i.coordinate_y, color= 'red')

    plt.savefig('Figure')
    plt.close(fig)

def PlotNode(G : Graph, nodename : str):
    import matplotlib.pyplot as plt

    fig = plt.figure()
    n : Node = GetNodeByName(G, nodename)

    for i in G.list_of_nodes:
        plt.scatter(i.coordinate_x, i.coordinate_y, color= 'gray')

    plt.scatter(n.coordinate_x, n.coordinate_y, color= 'green')

    for i in n.list_of_neighbors:
        line_x : list = [n.coordinate_x, i.coordinate_x]
        line_y : list = [n.coordinate_y, i.coordinate_y]

        plt.plot(line_x, line_y, color= 'red')

    plt.savefig('Figure_1')  # Save the figure
    plt.show()
    plt.close(fig)

def ImportData(G : Graph):
    from tkinter import filedialog  

    file_path = filedialog.askopenfilename(title="Select a TXT file",filetypes=[("Text Files", "*.txt")])

    try:
        with open(file_path, 'r') as Data:
            lines = [line.strip() for line in Data.readlines() if line.strip()]  # Remove empty lines and strip whitespace

            for i in lines:
                line = i.split(' ')

                if len(list(line[0])) == 1:
                    n = Node(line[0], int(line[1]), int(line[2]))
                    AddNode(G, n)

                elif len(list(line[0])) == 2:
                    AddSegment(G, line[0], line[1], line[2].strip())
    except Exception as e:
        print(f"Error reading file: {e}")
    
    


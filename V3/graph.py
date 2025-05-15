from node import *
from segment import *
from path import Path, AddNodeToPath, ContainsNode, PlotPath

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
    
def GetReachableNodes(G: Graph, start_node: Node) -> list:
    """Returns a list of all nodes that can be reached from start_node"""
    visited = set()
    to_visit = [start_node]
    
    while to_visit:
        current = to_visit.pop(0)
        if current not in visited:
            visited.add(current)
            # Add all unvisited neighbors to the queue
            for neighbor in current.list_of_neighbors:
                if neighbor not in visited:
                    to_visit.append(neighbor)
    
    return list(visited)

def FindShortestPath(G: Graph, origin: Node, destination: Node) -> Path:
    """Returns a Path describing the shortest path between origin and destination.
    Returns None if there is no path connecting these nodes."""
    if origin not in G.list_of_nodes or destination not in G.list_of_nodes:
        return None
        
    # Initialize the list of paths with the origin node
    current_paths = [Path(origin)]
    
    while current_paths:
        # Find the path with the lowest estimated cost
        best_path = min(current_paths, key=lambda p: p.get_estimated_cost(destination))
        current_paths.remove(best_path)
        
        # If we've reached the destination, we're done
        if best_path.get_last_node() == destination:
            return best_path
            
        # Try to extend the path with each neighbor
        for neighbor in best_path.get_last_node().list_of_neighbors:
            # Skip if neighbor is already in the path (avoid cycles)
            if ContainsNode(best_path, neighbor):
                continue
                
            # Create new path with this neighbor
            new_path = AddNodeToPath(best_path, neighbor)
            
            # Check if we already have a better path to this neighbor
            better_path_exists = False
            paths_to_remove = []
            
            for existing_path in current_paths:
                if (existing_path.get_last_node() == neighbor and 
                    existing_path.get_total_cost() <= new_path.get_total_cost()):
                    better_path_exists = True
                    break
                elif (existing_path.get_last_node() == neighbor and 
                      existing_path.get_total_cost() > new_path.get_total_cost()):
                    paths_to_remove.append(existing_path)
            
            # Remove worse paths
            for path in paths_to_remove:
                current_paths.remove(path)
            
            # Add the new path if no better path exists
            if not better_path_exists:
                current_paths.append(new_path)
    
    # If we get here, no path was found
    return None

def PlotReachability(G: Graph, start_node: Node):
    """Plots the graph highlighting reachable nodes from start_node"""
    import matplotlib.pyplot as plt
    
    reachable = GetReachableNodes(G, start_node)
    
    plt.clf()
    fig = plt.figure()
    
    # Plot all nodes in gray
    for node in G.list_of_nodes:
        plt.scatter(node.coordinate_x, node.coordinate_y, color='gray')
    
    # Plot all segments in gray
    for segment in G.list_of_segments:
        line_x = [segment.origin_node.coordinate_x, segment.destination_node.coordinate_x]
        line_y = [segment.origin_node.coordinate_y, segment.destination_node.coordinate_y]
        plt.plot(line_x, line_y, color='gray', alpha=0.3)
    
    # Plot reachable nodes in green
    for node in reachable:
        plt.scatter(node.coordinate_x, node.coordinate_y, color='green', s=100)
    
    # Plot segments between reachable nodes in red
    for segment in G.list_of_segments:
        if segment.origin_node in reachable and segment.destination_node in reachable:
            line_x = [segment.origin_node.coordinate_x, segment.destination_node.coordinate_x]
            line_y = [segment.origin_node.coordinate_y, segment.destination_node.coordinate_y]
            plt.plot(line_x, line_y, color='red', linewidth=2)
    
    plt.savefig('Figure_3')
    plt.close(fig)
    
    


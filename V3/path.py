from node import Node
import matplotlib.pyplot as plt

class Path:
    def __init__(self, origin_node: Node):
        self.nodes = [origin_node]  # List of nodes in the path
        self.cost = 0  # Total cost of the path
        
    def get_last_node(self) -> Node:
        return self.nodes[-1]
        
    def get_total_cost(self) -> float:
        return self.cost
        
    def get_estimated_cost(self, destination: Node) -> float:
        """Returns the total cost plus estimated cost to destination"""
        from node import Distance
        return self.cost + Distance(self.get_last_node(), destination)

def AddNodeToPath(path: Path, node: Node) -> Path:
    """Adds a node to the path and updates the cost"""
    from node import Distance
    new_path = Path(path.nodes[0])  # Create new path with same origin
    new_path.nodes = path.nodes.copy()  # Copy existing nodes
    new_path.nodes.append(node)  # Add new node
    new_path.cost = path.cost + Distance(path.get_last_node(), node)  # Update cost
    return new_path

def ContainsNode(path: Path, node: Node) -> bool:
    """Returns True if the Node is in the Path and False otherwise"""
    return node in path.nodes

def CostToNode(path: Path, node: Node) -> float:
    """Returns the total cost from the origin of the Path to the Node.
    Returns -1 if the Node is not in the Path."""
    if not ContainsNode(path, node):
        return -1
        
    from node import Distance
    total_cost = 0
    for i in range(len(path.nodes) - 1):
        if path.nodes[i] == node:
            break
        total_cost += Distance(path.nodes[i], path.nodes[i + 1])
    return total_cost

def PlotPath(graph, path: Path):
    """Plots the Path in the Graph"""
    plt.clf()
    fig = plt.figure()
    
    # Plot all nodes in gray
    for node in graph.list_of_nodes:
        plt.scatter(node.coordinate_x, node.coordinate_y, color='gray')
    
    # Plot all segments in gray
    for segment in graph.list_of_segments:
        line_x = [segment.origin_node.coordinate_x, segment.destination_node.coordinate_x]
        line_y = [segment.origin_node.coordinate_y, segment.destination_node.coordinate_y]
        plt.plot(line_x, line_y, color='gray', alpha=0.3)
    
    # Plot path nodes in green
    for node in path.nodes:
        plt.scatter(node.coordinate_x, node.coordinate_y, color='green', s=100)
    
    # Plot path segments in red
    for i in range(len(path.nodes) - 1):
        line_x = [path.nodes[i].coordinate_x, path.nodes[i + 1].coordinate_x]
        line_y = [path.nodes[i].coordinate_y, path.nodes[i + 1].coordinate_y]
        plt.plot(line_x, line_y, color='red', linewidth=2)
    
    plt.savefig('Figure_2')
    plt.close(fig) 
from node import *

class Segment:
    
    def __init__(self, name : str, origin_node : Node, destination_node : Node):
        from node import Distance

        self.name : str = name
        self.origin_node : Node = origin_node
        self.destination_node : Node = destination_node
        self.cost : float = Distance(origin_node, destination_node)

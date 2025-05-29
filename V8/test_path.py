from path import *
from test_graph import G, G2
from graph import GetReachableNodes, FindShortestPath, PlotReachability

def test_path_creation():
    # Test creating a path from a node
    node = G.list_of_nodes[0]  # Get first node
    path = Path(node)
    assert path.nodes == [node]
    assert path.cost == 0
    
    # Test adding a node to path
    next_node = node.list_of_neighbors[0]
    new_path = AddNodeToPath(path, next_node)
    assert len(new_path.nodes) == 2
    assert new_path.nodes[0] == node
    assert new_path.nodes[1] == next_node
    assert new_path.cost > 0
    
    print("Path creation tests passed!")

def test_path_operations():
    # Create a path with multiple nodes
    node = G.list_of_nodes[0]
    path = Path(node)
    for neighbor in node.list_of_neighbors[:2]:  # Add first two neighbors
        path = AddNodeToPath(path, neighbor)
    
    # Test ContainsNode
    assert ContainsNode(path, node)
    assert ContainsNode(path, path.nodes[1])
    assert not ContainsNode(path, G.list_of_nodes[-1])  # Some node not in path
    
    # Test CostToNode
    assert CostToNode(path, node) == 0  # Cost to start node is 0
    assert CostToNode(path, path.nodes[1]) > 0  # Cost to other nodes should be positive
    assert CostToNode(path, G.list_of_nodes[-1]) == -1  # Node not in path
    
    print("Path operations tests passed!")

def test_reachability():
    # Test reachability from a node
    start_node = G.list_of_nodes[0]
    reachable = GetReachableNodes(G, start_node)
    
    # Start node should be reachable
    assert start_node in reachable
    
    # All neighbors should be reachable
    for neighbor in start_node.list_of_neighbors:
        assert neighbor in reachable
    
    # Test with a different graph
    start_node = G2.list_of_nodes[0]
    reachable = GetReachableNodes(G2, start_node)
    assert start_node in reachable
    
    print("Reachability tests passed!")

def test_shortest_path():
    # Test finding shortest path between two nodes
    origin = G.list_of_nodes[0]
    destination = G.list_of_nodes[-1]
    
    path = FindShortestPath(G, origin, destination)
    if path:
        assert path.nodes[0] == origin
        assert path.nodes[-1] == destination
        assert len(path.nodes) > 1
        
        # Test that the path is continuous
        for i in range(len(path.nodes) - 1):
            assert path.nodes[i+1] in path.nodes[i].list_of_neighbors
    
    # Test with non-existent path
    # Create a disconnected node
    isolated_node = Node("Z", 100, 100)
    path = FindShortestPath(G, origin, isolated_node)
    assert path is None
    
    print("Shortest path tests passed!")

def run_all_tests():
    print("Running path tests...")
    test_path_creation()
    test_path_operations()
    test_reachability()
    test_shortest_path()
    print("All tests passed!")

if __name__ == "__main__":
    run_all_tests() 
import heapq
import json

class Node:
    def __init__(self, name):
        self.name = name
        self.adjacencies_list = []
        self.shortest_distance = float('inf')
        self.predecessor = None

class Edge:
    def __init__(self, weight, start_vertex, target_vertex):
        self.weight = weight
        self.start_vertex = start_vertex
        self.target_vertex = target_vertex

class Graph:
    def __init__(self):
        self.nodes = []
        self.edges = []

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, start_node, end_node, weight):
        edge = Edge(weight, start_node, end_node)
        self.edges.append(edge)
        start_node.adjacencies_list.append(edge)

    def dijkstra(self, start_node):

        queue = [] # heap
        start_node.shortest_distance = 0 # set the start node distance to 0
        heapq.heappush(queue, (0, start_node)) # push the start node to the heap

        while len(queue) > 0:
            current_distance, current_node = heapq.heappop(queue) # pop the node with the smallest distance

            if current_distance > current_node.shortest_distance:
                continue

            for edge in current_node.adjacencies_list:
                neighbor = edge.target_vertex
                new_distance = current_distance + edge.weight # calculate the new distance

                if new_distance < neighbor.shortest_distance:
                    neighbor.predecessor = current_node # update the predecessor
                    neighbor.shortest_distance = new_distance # update the distance
                    heapq.heappush(queue, (new_distance, neighbor)) # push the neighbor to the heap

    def shortest_path(self, start_node, end_node):
        self.dijkstra(start_node)
        node = end_node
        path = []

        while node is not None:
            path.append(node.name)
            node = node.predecessor

        return path[::-1]  # Reverse the list

def load_graph_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        node_dict = {name: Node(name) for name in data['nodes']}
        graph = Graph()

        for name, node in node_dict.items():
            graph.add_node(node)

        for edge in data['edges']:
            start_node = node_dict[edge['start']]
            end_node = node_dict[edge['end']]
            weight = edge['weight']
            graph.add_edge(start_node, end_node, weight)

        return graph, node_dict

# Usage
graph, node_dict = load_graph_from_json('/Users/saiyingge/Downloads/graph_data.json')
# calculate the shortest path from A to C
start_node = node_dict['A']
end_node = node_dict['C']
print(graph.shortest_path(start_node, end_node))

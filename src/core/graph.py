from typing import Dict, List
from collections import namedtuple
import json
from sys import maxsize as INT_MAX
import random
from .node import Node, SerializedNode, NODE_NOT_FOUND_ERROR

class SerializedGraph:
    def __init__(self) -> None:
        self.nodes: List[SerializedNode] = []

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def save_to_file(self, file_path: str) -> None:
        with open(file_path, "w") as file:
            file.write(self.to_json())

    @staticmethod
    def from_json(json_string: str) -> "SerializedGraph":
        #https://stackoverflow.com/questions/6578986/how-to-convert-json-data-into-a-python-object
        # res = json.loads(json_string, object_hook=lambda d: SerializedGraph(**d)) #This would through an unexpected kwarg error.
        obj = json.loads(json_string, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
        return obj

    @staticmethod
    def load_from_file(file_path: str) -> "Graph":
        with open(file_path, "r") as file:
            serialized_graph = SerializedGraph.from_json(file.read())
            return Graph.deserialize(serialized_graph)

class Graph:
    #Public get, private set.
    @property
    def nodes(self) -> Dict[int, Node]:
        """The nodes on the graph."""
        return self.__nodes

    def __init__(self) -> None:
        self.__nodes: Dict[int, Node] = {}

    def add_node(self) -> Node:
        """Adds a node to the graph."""
        id = 0
        while id == 0 or id in self.__nodes:
            id = random.randint(0, INT_MAX)

        node = Node(id)
        self.__nodes[id] = node

        return node

    def remove_node(self, node: Node) -> None:
        """Removes a node from the graph."""
        if node.id not in self.__nodes:
            raise KeyError(NODE_NOT_FOUND_ERROR)

        for neighbor in node.adjacency_list.keys():
            neighbor.remove_edge(node)

        del self.__nodes[node.id]

    def add_edge(self, node1: Node, node2: Node, weight: int = 1) -> None:
        """Adds an edge to the graph."""
        node1.add_edge(node2, weight)
        node2.add_edge(node1, weight)

    def update_edge_weight(self, node1: Node, node2: Node, weight: int) -> None:
        """Updates the weight of an edge in the graph."""
        node1.update_edge_weight(node2, weight)
        node2.update_edge_weight(node1, weight)

    def remove_edge(self, node1: Node, node2: Node) -> None:
        """Removes an edge from the graph."""
        node1.remove_edge(node2)
        node2.remove_edge(node1)

    def serialize(self) -> SerializedGraph:
        serialized_graph = SerializedGraph()
        serialized_graph.nodes = [node.serialize() for node in self.nodes.values()]
        return serialized_graph

    @staticmethod
    def deserialize(serialized_graph: SerializedGraph) -> "Graph":
        graph = Graph()

        for serialized_node in serialized_graph.nodes:
            node = Node.deserialize(serialized_node)
            graph.nodes[node.id] = node

        for serialized_node in serialized_graph.nodes:
            node = graph.nodes[serialized_node.id]
            for edge in serialized_node.adjacencyList:
                neighbouring_node = graph.nodes[edge.neighbouringNodeID]
                node.add_edge(neighbouring_node, edge.weight)

        return graph

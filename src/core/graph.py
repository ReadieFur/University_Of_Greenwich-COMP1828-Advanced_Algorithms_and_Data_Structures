from typing import Dict, List
import json
from sys import maxsize as INT_MAX
import random
from .node import Node, SerializedNode, NODE_NOT_FOUND_ERROR
from .node import Edge

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
        obj = json.loads(json_string)
        graph = SerializedGraph()
        graph.nodes = [SerializedNode.from_obj(node) for node in obj["nodes"]]
        return graph

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

    @property
    def edge_list(self) -> Dict[int, tuple[Node, Node, Edge]]:
        """The edges on the graph."""
        return self.__edge_list

    def __init__(self) -> None:
        self.__nodes: Dict[int, Node] = {}
        self.__edge_list: Dict[int, tuple[Node, Node, Edge]] = {}

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

        for neighbor in node.adjacency_dict.items():
            self.nodes[neighbor[0]].remove_all_edges(node)

        del self.__nodes[node.id]

    def add_edge(self, node1: Node, node2: Node, weight: int, id: int | None = None) -> Edge:
        """Adds an edge to the graph."""
        if id is None:
            id = 0
            while id == 0 or id in self.__edge_list:
                id = random.randint(0, INT_MAX)
        elif id in self.__edge_list:
            raise KeyError(f"Edge with ID {id} already exists.")

        edge = Edge(id, weight)
        self.__edge_list[id] = (node1, node2, edge)

        node1.add_edge(node2, edge)
        node2.add_edge(node1, edge)

        return edge

    def remove_edge(self, edge: Edge) -> None:
        """Removes an edge from the graph."""
        if edge not in self.__edge_list:
            raise KeyError(f"Edge with ID {edge.id} not found.")

        node1, node2, _ = self.__edge_list[edge.id]
        node1.remove_edge(node2, edge)
        node2.remove_edge(node1, edge)

        del self.__edge_list[edge.id]

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
            for neighbour_node_id, serialized_edges in serialized_node.adjacencyList.items():
                for serialized_edge in serialized_edges:
                    neighbour_node = graph.nodes[int(neighbour_node_id)]
                    try:
                        graph.add_edge(node, neighbour_node, serialized_edge.weight, serialized_edge.id)
                    except KeyError:
                        pass

        return graph

from typing import Dict, List
import json
import random
from core.graph import Graph, SerializedGraph, INT_MAX
from .tubemap_node import TubemapNode, SerializedTubemapNode
from .tubemap_edge import TubemapEdge

class SerializedTubemapGraph(SerializedGraph):
    def __init__(self) -> None:
        self.nodes: List[SerializedTubemapNode] = []

    @staticmethod
    def from_json(json_string: str) -> "SerializedTubemapGraph":
        obj = json.loads(json_string)
        graph = SerializedTubemapGraph()
        graph.nodes = [SerializedTubemapNode.from_obj(node) for node in obj["nodes"]]
        return graph

    @staticmethod
    def load_from_file(file_path: str) -> "TubemapGraph":
        with open(file_path, "r") as file:
            serialized_graph = SerializedTubemapGraph.from_json(file.read())
            return TubemapGraph.deserialize(serialized_graph)

class TubemapGraph(Graph):
    @property
    def nodes(self) -> Dict[int, TubemapNode]:
        return super().nodes

    @property
    def edge_list(self) -> Dict[int, tuple[TubemapNode, TubemapNode, TubemapEdge]]:
        return super().edge_list

    def __init__(self) -> None:
        super().__init__()
        # self.__nodes: Dict[int, TubemapNode] = {}
        # self.__edge_list: Dict[int, tuple[TubemapNode, TubemapNode, TubemapEdge]] = {}

    def add_node(self) -> TubemapNode:
        """Adds a node to the graph."""
        id = 0
        while id == 0 or id in self.__nodes:
            id = random.randint(0, INT_MAX)

        node = TubemapNode(id)
        self.__nodes[id] = node

        return node

    def add_edge(self, node1: TubemapNode, node2: TubemapNode, weight: int, id: int | None = None) -> TubemapEdge:
        """Adds an edge to the graph."""
        if id is None:
            id = 0
            while id == 0 or id in self.edge_list:
                id = random.randint(0, INT_MAX)
        elif id in self.edge_list:
            raise KeyError(f"Edge with ID {id} already exists.")

        edge = TubemapEdge(id, weight)
        self.edge_list[id] = (node1, node2, edge)

        node1.add_edge(node2, edge)
        node2.add_edge(node1, edge)

        return edge

    def serialize(self) -> SerializedTubemapGraph:
        base_serialized_graph = super().serialize()
        serialized_graph = SerializedTubemapGraph()
        serialized_graph.nodes = base_serialized_graph.nodes
        return serialized_graph

    @staticmethod
    def deserialize(serialized_graph: SerializedTubemapGraph) -> "TubemapGraph":
        graph = TubemapGraph()

        for serialized_node in serialized_graph.nodes:
            node = TubemapNode.deserialize(serialized_node)
            graph.nodes[node.id] = node

        for serialized_node in serialized_graph.nodes:
            node = graph.nodes[serialized_node.id]
            for neighbour_node_id, serialized_edges in serialized_node.adjacencyList.items():
                for serialized_edge in serialized_edges:
                    neighbour_node = graph.nodes[int(neighbour_node_id)]
                    try:
                        edge = graph.add_edge(node, neighbour_node, serialized_edge.weight, serialized_edge.id)
                        edge.closed = serialized_edge.closed
                        edge.label = serialized_edge.label
                    except KeyError:
                        pass

        return graph

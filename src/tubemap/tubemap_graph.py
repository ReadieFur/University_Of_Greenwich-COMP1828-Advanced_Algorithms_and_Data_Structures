from typing import Dict, List
from core.graph import Graph, SerializedGraph
from .tubemap_node import TubemapNode, SerializedTubemapNode

class SerializedTubemapGraph(SerializedGraph):
    def __init__(self) -> None:
        self.nodes: List[SerializedTubemapNode] = {}

    @staticmethod
    def from_json(json_string: str) -> "SerializedTubemapGraph":
        return SerializedGraph.from_json(json_string)

    @staticmethod
    def load_from_file(file_path: str) -> "TubemapGraph":
        with open(file_path, "r") as file:
            serialized_graph = SerializedTubemapGraph.from_json(file.read())
            return TubemapGraph.deserialize(serialized_graph)

class TubemapGraph(Graph):
    @property
    def nodes(self) -> Dict[int, TubemapNode]:
        return super().nodes

    def update_edge_availability(node1: TubemapNode, node2: TubemapNode, is_available: bool) -> None:
        node1.update_edge_availability(node2, is_available)
        node2.update_edge_availability(node1, is_available)

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
            for edge in serialized_node.adjacencyList:
                neighbouring_node = graph.nodes[edge.neighbouringNodeID]
                node.add_edge(neighbouring_node, edge.weight)

        return graph

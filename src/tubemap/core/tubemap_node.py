from typing import Dict, List, Any
from core.node import Node, SerializedNode
from .tubemap_edge import TubemapEdge, SerializedTubemapEdge

class SerializedTubemapNode(SerializedNode):
    def __init__(self) -> None:
        super().__init__()
        self.adjacencyList: Dict[str, List[SerializedTubemapEdge]] = {}
        self.label = ""

    @staticmethod
    def from_obj(obj: Dict[str, Any]) -> "SerializedTubemapNode":
        node = SerializedTubemapNode()
        node.id = obj["id"]
        adjacency_list: Dict[str, List[SerializedTubemapEdge]] = {}
        for key, value in obj["adjacencyList"].items():
            adjacency_list[key] = [SerializedTubemapEdge.from_obj(edge) for edge in value]
        node.adjacencyList = adjacency_list
        if "label" in obj:
            node.label = obj["label"]
        return node

class TubemapNode(Node):
    @property
    def adjacency_dict(self) -> Dict[int, Dict[int, TubemapEdge]]:
        """The adjacency list of the node."""
        return super().adjacency_dict

    def __init__(self, id: int):
        super().__init__(id)
        # self.__adjacency_dict: Dict[int, Dict[int, TubemapEdge]] = {}
        self.label = ""

    def serialize(self) -> SerializedNode:
        adjacency_list: Dict[str, List[SerializedTubemapEdge]] = {}

        for neighbour_node_id, edge_dict in self.adjacency_dict.items():
            adjacency_list[str(neighbour_node_id)] = []
            for edge in edge_dict.values():
                adjacency_list[str(neighbour_node_id)].append(edge.serialize())

        serialized_node = SerializedTubemapNode()
        serialized_node.id = self.id
        serialized_node.adjacencyList = adjacency_list
        serialized_node.label = self.label
        return serialized_node

    @staticmethod
    def deserialize(serialized_node: SerializedTubemapNode) -> "TubemapNode":
        node = TubemapNode(serialized_node.id)
        if hasattr(serialized_node, "label"):
            node.label = serialized_node.label
        return node

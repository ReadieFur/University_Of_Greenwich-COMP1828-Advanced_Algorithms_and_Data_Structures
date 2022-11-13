from typing import Dict, List
from core.node import Node, SerializedNode
from .tubemap_edge import TubemapEdge, SeralizedTubemapEdge

class SerializedTubemapNode(SerializedNode):
    def __init__(self) -> None:
        super().__init__()
        self.adjacencyList: List[SeralizedTubemapEdge] = []
        self.tag = ""

class TubemapNode(Node):
    @property
    def adjacency_list(self) -> Dict["TubemapNode", TubemapEdge]:
        """The adjacency list of the node."""
        return self.__adjacency_list

    def __init__(self, id: int):
        super().__init__(id)
        self.__adjacency_list: Dict["TubemapNode", TubemapEdge] = {}
        self.tag = ""

    def add_edge(self, neibouring_node: "Node", weight: int = 1) -> None:
        self.__adjacency_list[neibouring_node] = TubemapEdge(neibouring_node, weight)

    def update_edge_availability(self, node: "TubemapNode", is_available: bool) -> None:
        self.adjacency_list[node].closed = not is_available

    def serialize(self) -> SerializedNode:
        base_serialized_node = super().serialize()
        serialized_node = SerializedTubemapNode()
        serialized_node.id = base_serialized_node.id
        serialized_node.adjacencyList = base_serialized_node.adjacencyList
        serialized_node.tag = self.tag
        return serialized_node

    @staticmethod
    def deserialize(serialized_node: SerializedTubemapNode) -> "TubemapNode":
        node = TubemapNode(serialized_node.id)
        if hasattr(serialized_node, "tag"):
            node.tag = serialized_node.tag
        return node

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .tubemap_node import TubemapNode
from core.edge import Edge, SerializedEdge

class SeralizedTubemapEdge(SerializedEdge):
    def __init__(self) -> None:
        super().__init__()
        self.closed = False

class TubemapEdge(Edge):
    def __init__(self, neibouring_node: TubemapNode, weight: int = 1):
        super().__init__(neibouring_node, weight)
        self.closed = False

    def serialize(self) -> SeralizedTubemapEdge:
        base_serialized_edge = super().serialize()
        serialized_edge = SeralizedTubemapEdge()
        serialized_edge.neighbouringNodeID = base_serialized_edge.neighbouringNodeID
        serialized_edge.weight = base_serialized_edge.weight
        serialized_edge.closed = self.closed
        return serialized_edge

    @staticmethod
    def deserialize(serialized_edge: SeralizedTubemapEdge, node: TubemapNode) -> TubemapEdge:
        edge = TubemapEdge(node)
        edge.weight = serialized_edge.weight
        if hasattr(serialized_edge, "closed"):
            edge.closed = serialized_edge.closed
        return edge

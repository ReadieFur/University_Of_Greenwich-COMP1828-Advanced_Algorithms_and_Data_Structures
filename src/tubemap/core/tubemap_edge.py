from typing import Dict, Any
from core.edge import Edge, SerializedEdge

class SerializedTubemapEdge(SerializedEdge):
    def __init__(self) -> None:
        super().__init__()
        self.closed = False
        self.label = ""

    @staticmethod
    def from_obj(obj: Dict[str, Any]) -> "SerializedTubemapEdge":
        edge = SerializedTubemapEdge()
        edge.id = obj["id"]
        edge.weight = obj["weight"]
        if "closed" in obj:
            edge.closed = obj["closed"]
        if "label" in obj:
            edge.label = obj["label"]
        return edge

class TubemapEdge(Edge):
    def __init__(self, id: int, weight: int = 1):
        super().__init__(id, weight)
        self.closed = False
        self.label = ""

    def serialize(self) -> SerializedTubemapEdge:
        base_serialized_edge = super().serialize()
        serialized_edge = SerializedTubemapEdge()
        serialized_edge.id = base_serialized_edge.id
        serialized_edge.weight = base_serialized_edge.weight
        serialized_edge.closed = self.closed
        return serialized_edge

    @staticmethod
    def deserialize(serialized_edge: SerializedTubemapEdge) -> "TubemapEdge":
        edge = TubemapEdge(serialized_edge.id, serialized_edge.weight)
        if hasattr(serialized_edge, "closed"):
            edge.closed = serialized_edge.closed
        if hasattr(serialized_edge, "label"):
            edge.label = serialized_edge.label
        return edge

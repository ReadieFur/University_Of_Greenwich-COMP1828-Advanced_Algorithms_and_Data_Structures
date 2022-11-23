from typing import Dict, Any

class SerializedEdge:
    def __init__(self) -> None:
        self.id: int = 0
        self.weight: int = 0

    @staticmethod
    def from_obj(obj: Dict[str, Any]) -> "SerializedEdge":
        edge = SerializedEdge()
        edge.id = obj["id"]
        edge.weight = obj["weight"]
        return edge

class Edge:
    #Public get, private set.
    @property
    def id(self) -> int:
        """The id of the edge."""
        return self.__id

    def __init__(self, id: int, weight: int = 1):
        self.__id: int = id
        self.weight: int = weight

    def serialize(self) -> SerializedEdge:
        serialized_edge = SerializedEdge()
        serialized_edge.id = self.id
        serialized_edge.weight = self.weight
        return serialized_edge

    @staticmethod
    def deserialize(serialized_edge: SerializedEdge) -> "Edge":
        return Edge(serialized_edge.id, serialized_edge.weight)

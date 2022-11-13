#Avoid circular import (this import is only used for IDE type hinting).
#https://stackoverflow.com/questions/39740632/python-type-hinting-without-cyclic-imports
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .node import Node

class SerializedEdge:
    def __init__(self) -> None:
        self.neighbouringNodeID: int = 0
        self.weight: int = 0

class Edge:
    #Public get, private set.
    @property
    def neibouring_node(self) -> Node:
        """The neibouring that this edge is connected to."""
        return self.__neibouring_node

    def __init__(self, neibouring_node: Node, weight: int = 1):
        self.__neibouring_node: Node = neibouring_node
        self.weight: int = weight

    def serialize(self) -> SerializedEdge:
        serialized_edge = SerializedEdge()
        serialized_edge.neighbouringNodeID = self.neibouring_node.id
        serialized_edge.weight = self.weight
        return serialized_edge

    @staticmethod
    def deserialize(serialized_edge: SerializedEdge, node: Node) -> Edge:
        edge = Edge(node)
        edge.weight = serialized_edge.weight
        return edge

from typing import List
from core.graph import Graph
from core.node import Node
from core.edge import Edge

class PathPart:
    @property
    def node(self) -> Node:
        return self.__node

    @property
    def edge(self) -> Edge:
        return self.__edge

    def __init__(self, node: Node, edge: Edge | None) -> None:
        self.__node: Node = node
        self.__edge: Edge | None = edge

class AAlgorithm:
    @staticmethod
    def find_shortest_path(start_node: Node, end_node: Node, graph: Graph) -> List[PathPart]:
        raise NotImplementedError("Abstract method not implemented.")

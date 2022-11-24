from typing import List
from sys import maxsize as INT_MAX
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

class AlgorithmNode:
    @property
    def node(self) -> Node:
        return self.__node

    def __init__(self, node: Node) -> None:
        self.__node: Node = node
        self.path_weight: int = INT_MAX
        self.previous_node: "AlgorithmNode" | None = None
        self.previous_edge: Edge | None = None

    @staticmethod
    def to_path_array(dijkstra_node: "AlgorithmNode") -> List[PathPart]:
        path_array: List[PathPart] = []

        current_node = dijkstra_node
        previous_edge: Edge | None = None
        while current_node is not None:
            path_array.append(PathPart(current_node.node, previous_edge))

            previous_edge = current_node.previous_edge

            if current_node.previous_node is None:
                break

            current_node = current_node.previous_node

        path_array.reverse()
        return path_array


class AAlgorithm:
    @staticmethod
    def find_shortest_path(graph: Graph, start_node: Node, end_node: Node) -> List[PathPart]:
        raise NotImplementedError("Abstract method not implemented.")


from typing import Any
from core.graph import Graph
from core.node import Node

class AAlgorithm:
    @staticmethod
    def find_shortest_path(start_node: Node, end_node: Node, graph: Graph) -> Any:
        raise NotImplementedError("Abstract method not implemented.")

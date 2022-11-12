from typing import Dict
from sys import maxsize as INT_MAX
import random
from .node import Node, NODE_NOT_FOUND_ERROR

class Graph:
    #Public get, private set.
    __nodes: Dict[int, Node] = {}
    @property
    def nodes(self):
        """The nodes on the graph."""
        return self.__nodes

    def add_node(self) -> Node:
        """Adds a node to the graph."""
        id = 0
        while id == 0 or id in self.__nodes:
            id = random.randint(0, INT_MAX)

        node = Node(id)
        self.__nodes[id] = node

        return node

    def remove_node(self, node: Node) -> None:
        """Removes a node from the graph."""
        if node.id not in self.__nodes:
            raise KeyError(NODE_NOT_FOUND_ERROR)

        for neighbor in node.adjacency_list.keys():
            neighbor.remove_edge(node)

        del self.__nodes[node.id]

    def add_edge(self, node1: Node, node2: Node, weight: int = 1) -> None:
        """Adds an edge to the graph."""
        node1.add_edge(node2, weight)
        node2.add_edge(node1, weight)

    def update_edge_weight(self, node1: Node, node2: Node, weight: int) -> None:
        """Updates the weight of an edge in the graph."""
        node1.update_edge_weight(node2, weight)
        node2.update_edge_weight(node1, weight)

    def remove_edge(self, node1: Node, node2: Node) -> None:
        """Removes an edge from the graph."""
        node1.remove_edge(node2)
        node2.remove_edge(node1)

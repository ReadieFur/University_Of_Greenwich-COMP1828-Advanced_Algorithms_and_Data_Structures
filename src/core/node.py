from typing import Dict, List
from .edge import Edge, SerializedEdge

NODE_NOT_FOUND_ERROR = "The node is not in the adjacency list."

class SerializedNode:
    def __init__(self) -> None:
        self.id: int = 0
        self.adjacencyList: List[SerializedEdge] = []

class Node:
    #Public get, private set.
    @property
    def id(self) -> int:
        """The id of the node"""
        return self.__id

    #As I am used to working in type strict languages, it was odd to see that I cannot reference to typeof(self), after a quick research online I found that you can wrap the type name in a string literal to work around this: https://stackoverflow.com/questions/3877947/self-referencing-classes-in-python
    #Public get, private set.
    @property
    def adjacency_list(self) -> Dict["Node", Edge]:
        """The adjacency list of the node."""
        return self.__adjacency_list

    def __init__(self, id: int):
        self.__id: int = id
        self.__adjacency_list: Dict["Node", Edge] = {}

    def add_edge(self, neibouring_node: "Node", weight: int = 1) -> None:
        """Adds an edge to the adjacency list."""
        self.__adjacency_list[neibouring_node] = Edge(neibouring_node, weight)

    def update_edge_weight(self, neibouring_node: "Node", weight: int) -> None:
        """Updates the weight of an edge in the adjacency list."""
        if neibouring_node not in self.__adjacency_list:
            raise KeyError(NODE_NOT_FOUND_ERROR)
        self.__adjacency_list[neibouring_node].weight = weight

    def remove_edge(self, neibouring_node: "Node") -> None:
        """Removes an edge from the adjacency list."""
        if neibouring_node not in self.__adjacency_list:
            raise KeyError(NODE_NOT_FOUND_ERROR)
        del self.__adjacency_list[neibouring_node]

    def serialize(self) -> SerializedNode:
        serialized_node = SerializedNode()
        serialized_node.id = self.id
        serialized_node.adjacencyList = [edge.serialize() for edge in self.adjacency_list.values()]
        return serialized_node

    @staticmethod
    def deserialize(serialized_node: SerializedNode) -> "Node":
        node = Node(serialized_node.id)
        #Skip adding edges as their corresponding nodes may not exist yet.
        return node

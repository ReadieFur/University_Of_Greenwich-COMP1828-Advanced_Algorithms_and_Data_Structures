from typing import Dict, List, Any
from .edge import Edge, SerializedEdge

NODE_NOT_FOUND_ERROR = "The node is not in the adjacency list."

class SerializedNode:
    def __init__(self) -> None:
        self.id: int = 0
        self.adjacencyList: Dict[str, List[SerializedEdge]] = {}

    @staticmethod
    def from_obj(obj: Dict[str, Any]) -> "SerializedNode":
        node = SerializedNode()
        node.id = obj["id"]
        adjacency_list: Dict[str, List[SerializedEdge]] = {}
        for key, value in obj["adjacencyList"].items():
            adjacency_list[key] = [SerializedEdge.from_obj(edge) for edge in value]
        node.adjacencyList = adjacency_list
        return node

class Node:
    #Public get, private set.
    @property
    def id(self) -> int:
        """The id of the node"""
        return self.__id

    #As I am used to working in type strict languages, it was odd to see that I cannot reference to typeof(self), after a quick research online I found that you can wrap the type name in a string literal to work around this: https://stackoverflow.com/questions/3877947/self-referencing-classes-in-python
    #Public get, private set.
    @property
    def adjacency_dict(self) -> Dict[int, Dict[int, Edge]]:
        """The adjacency list of the node."""
        return self.__adjacency_dict

    def __init__(self, id: int):
        self.__id: int = id
        self.__adjacency_dict: Dict[int, Dict[int, Edge]] = {}

    def add_edge(self, neibouring_node: "Node", edge: Edge) -> None:
        """Adds an edge to the adjacency list."""
        if neibouring_node.id not in self.adjacency_dict:
            self.__adjacency_dict[neibouring_node.id] = {}
        self.__adjacency_dict[neibouring_node.id][edge.id] = edge

    def remove_edge(self, neibouring_node: "Node", edge: Edge) -> None:
        """Removes an edge from the adjacency list."""
        if neibouring_node.id not in self.adjacency_dict:
            return
        self.adjacency_dict[neibouring_node.id].pop(edge.id, None)

    def remove_all_edges(self, neibouring_node: "Node") -> None:
        """Removes all edges from the adjacency list for a specific node."""
        if neibouring_node.id not in self.adjacency_dict:
            return
        self.adjacency_dict.pop(neibouring_node.id, None)

    def serialize(self) -> SerializedNode:
        adjacency_list: Dict[str, List[SerializedEdge]] = {}

        for neighbour_node_id, edge_dict in self.adjacency_dict.items():
            adjacency_list[str(neighbour_node_id)] = []
            for edge in edge_dict.values():
                adjacency_list[str(neighbour_node_id)].append(edge.serialize())

        serialized_node = SerializedNode()
        serialized_node.id = self.id
        serialized_node.adjacencyList = adjacency_list
        return serialized_node

    @staticmethod
    def deserialize(serialized_node: SerializedNode) -> "Node":
        node = Node(serialized_node.id)
        #Skip adding edges as their corresponding nodes may not exist yet.
        return node

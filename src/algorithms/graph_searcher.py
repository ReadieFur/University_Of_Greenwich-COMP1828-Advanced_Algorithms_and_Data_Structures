from typing import List
from core.graph import Graph
from core.node import Node

class GraphSearcher:
    @staticmethod
    def _breadth_first_search(graph: Graph, node: Node, visited: List[Node]) -> None:
        """
        This search will visit all unvisited, connected nodes in the order they were added to the graph.
        Meaning that it will visit nodes neighbors in a queue-like fashion.
        """
        #We first start by adding the node to the queue.
        queue = [node]

        while len(queue) > 0:
            #Take the first node from the queue.
            current = queue.pop(0)

            #If the node has been visited, continue, otherwise mark it as visited.
            if current in visited:
                continue
            visited.append(current)

            #For each of the current node's neighbors, add them to the queue.
            for neibouring_node_id in current.adjacency_dict.keys():
                queue.append(graph.nodes[neibouring_node_id])

    @staticmethod
    def _depth_first_search(graph: Graph, node: Node, visited: List[Node]) -> None:
        """
        This search will visit all unvisited, connected nodes one after the other, recursively.
        Meaning that it will traverse one branch of the graph before moving on to the next.
        """
        #We can safley use the same visited Set when recursing becuase it is a data type and therefore is passed by reference, not a value, unlike a list.
        #If the node has been visited, return, otherwise mark it as visited.
        if node in visited:
            return
        visited.append(node)

        #For each of the current node's neighbors, recursively call the DFS function.
        for neibouring_node_id in node.adjacency_dict.keys():
            GraphSearcher._depth_first_search(graph, graph.nodes[neibouring_node_id], visited)

    @staticmethod
    def is_graph_connected(graph: Graph, useBFS: bool) -> bool:
        """If useBFS is false, then DFS is used instead."""
        #Both searches require a starting node which can be any arbitrary node in the graph, so we will just use the first one.
        starting_node = next(iter(graph.nodes.values()))
        visited: List[Node] = []

        if useBFS:
            GraphSearcher._breadth_first_search(graph, starting_node, visited)
        else:
            GraphSearcher._depth_first_search(graph, starting_node, visited)

        #We can tell if a graph is connected if the search returns a list of nodes whos size is equal to the number of nodes in the graph.
        return len(visited) == len(graph.nodes)

    @staticmethod
    def is_path_available(graph: Graph, start: Node, end: Node, useBFS: bool) -> bool:
        visited: List[Node] = []

        if useBFS:
            GraphSearcher._breadth_first_search(graph, start, visited)
        else:
            GraphSearcher._depth_first_search(graph, start, visited)

        #We can tell if a path is available if the search returns a list of nodes that contains the end node.
        return end in visited

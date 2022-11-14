from typing import Dict, List
from sys import maxsize as INT_MAX
from algorithms.algorithm import AAlgorithm
from core.graph import Graph
from core.node import Node

class DijkstraNode:
    @property
    def node(self) -> Node:
        return self.__node

    #Public get, public (custom) set.
    @property
    def is_boxed(self) -> bool:
        return self.__is_boxed
    @is_boxed.setter
    def is_boxed(self, value: bool) -> None:
        if self.__is_boxed:
            raise AssertionError("Node cannot be unboxed.")
        self.__is_boxed = value

    def __init__(self, node: Node) -> None:
        self.__node: Node = node
        self.previous_node: "DijkstraNode" = None
        self.path_weight: int = INT_MAX
        self.__is_boxed: bool = False

"""
* I am using the following psuedocode to assist in my creation of this algorithm:
* From: COMP1828 "Graph 2.pptx" slide 30:
# Input: A weighted connected graph G = (V, E) with nonnegative weights and its vertex s
# Output: The length dv of a shortest path from s to v and it's penultimate vertex pv for every vertex v in V
Algorithm (G, s)
    Initialize(Q) # initialize priority queue to empty
    for every vertex v in V
        dv <- INFINITY
        pv <- NULL
        Insert(Q, v, dv) # initialize vertex priority in the priority queue
    ds <- 0
    Decrease(Q, s, ds) # update priority of s with ds
    Vt <- 0/
    for i <- 0 to |V| - 1 do
        u* <- DeleteMin(Q) # delete the minimum priority element
        Vt <- Vt U {u*}
        for every vertex u in V - Vt that is adjacent to u* do
            if du + w(u*, u) < du
                du <- du + w(u*, u)
                pu <- u*
                Decrease(Q, u, du)
"""
class DijkstrasAlgorithm(AAlgorithm):
    @staticmethod
    def find_shortest_path(graph: Graph, start_node: Node, end_node: Node) -> DijkstraNode:
        dijkstra_nodes: Dict[int, DijkstraNode] = {}
        for i in graph.nodes.keys():
            dijkstra_node = DijkstraNode(graph.nodes[i])
            dijkstra_nodes[i] = dijkstra_node
        dijkstra_nodes[start_node.id].path_weight = 0

        #I use a for loop here instead of a while true loop to prevent the possibility of an infinite loop, though this should never happen...
        for _ in range(0, len(graph.nodes)):
            #region Find the known shortest path to the current node.
            lightest_node_id = 0
            lightest_path = INT_MAX
            for j in dijkstra_nodes.keys():
                dijkstra_node_j = dijkstra_nodes[j]

                if dijkstra_node_j.is_boxed or dijkstra_node_j.path_weight >= lightest_path:
                    continue

                lightest_node_id = j
                lightest_path = dijkstra_node_j.path_weight
            #endregion

            """
            * I create variables here with references to the Dijkstra node here.
             * This is done to save on time on what would be spent accessing the dictionary multiple times below.
             * As classes are passed by reference in C#, it is fine to assign to a new variable here as we store the reference to the object.
             * This however does come at the cost of slightly increased memory usage, though I do wonder if this creation on the heap is slower.
             * This can be seen being done in the loops above and below this too.
            """
            dijkstra_node = dijkstra_nodes[lightest_node_id]

            #As we have now explored all of this nodes neighbours (occurred in the previous iteration, except for the first), we can now box it.
            dijkstra_node.is_boxed = True

            #As the node we are working with past this point is boxed, if it is the node we are looking for, we can return here.
            if lightest_node_id == end_node.id:
                return dijkstra_node

            #region Update the path weight of this nodes unboxed neighbours.
            for k in dijkstra_node.node.adjacency_list.items():
                neighbouring_node = k[0]
                edge = k[1]

                dijkstra_edge_node = dijkstra_nodes[neighbouring_node.id]

                #If I haven't boxed this node and the new distance is less than the current distance + the edge weight...
                if dijkstra_edge_node.is_boxed or dijkstra_node.path_weight + edge.weight >= dijkstra_edge_node.path_weight:
                    continue

                #Update the edge node's distance from the start node using the current shortest path + this edges weight.
                dijkstra_edge_node.path_weight = dijkstra_node.path_weight + edge.weight
                dijkstra_edge_node.previous_node = dijkstra_node
            #endregion

        #If we do end somehow end up here, something has gone wrong.
        raise AssertionError(f"Failed to find a path from node '{start_node.id}' to node '{end_node.id}' on the specified graph.")

    @staticmethod
    def dijkstra_node_to_node_array(dijkstra_node: DijkstraNode) -> List[Node]:
        node_array: List[Node] = []

        while dijkstra_node is not None:
            node_array.append(dijkstra_node.node)

            if dijkstra_node.previous_node is None:
                break

            dijkstra_node = dijkstra_node.previous_node

        node_array.reverse()
        return node_array

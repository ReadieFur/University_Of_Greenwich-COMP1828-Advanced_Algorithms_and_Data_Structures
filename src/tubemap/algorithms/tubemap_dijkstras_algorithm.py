from typing import Dict, List
from sys import maxsize as INT_MAX
from tubemap.core.tubemap_graph import TubemapGraph
from tubemap.core.tubemap_node import TubemapNode
from algorithms.algorithm import AlgorithmNode, PathPart
from algorithms.dijkstras_algorithm import DijkstrasAlgorithm, DijkstraNode

class TubemapDijkstraNode(DijkstraNode):
    @property
    def node(self) -> TubemapNode:
        return super().node

    def __init__(self, node: TubemapNode) -> None:
        super().__init__(node)

class TubemapDijkstrasAlgorithm(DijkstrasAlgorithm):
    @staticmethod
    def find_shortest_path(graph: TubemapGraph, start_node: TubemapNode, end_node: TubemapNode) -> List[PathPart]:
        dijkstra_nodes: Dict[int, TubemapDijkstraNode] = {}
        for i in graph.nodes.keys():
            dijkstra_node = TubemapDijkstraNode(graph.nodes[i])
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
                return AlgorithmNode.to_path_array(dijkstra_node)

            #region Update the path weight of this nodes unboxed neighbours.
            for [neighbouring_node_id, edges] in dijkstra_node.node.adjacency_dict.items():
                dijkstra_edge_node = dijkstra_nodes[neighbouring_node_id]

                #If I haven't boxed this node and the new distance is less than the current distance + the edge weight...
                if dijkstra_edge_node.is_boxed:
                    continue

                for edge in edges.values():
                    if dijkstra_node.path_weight + edge.weight >= dijkstra_edge_node.path_weight or edge.closed:
                        continue

                    #Update the edge node's distance from the start node using the current shortest path + this edges weight.
                    dijkstra_edge_node.path_weight = dijkstra_node.path_weight + edge.weight
                    dijkstra_edge_node.previous_node = dijkstra_node
                    dijkstra_edge_node.previous_edge = edge
        #endregion

        #If we do end somehow end up here, something has gone wrong.
        raise AssertionError(f"Failed to find a path from node '{start_node.id}' to node '{end_node.id}' on the specified graph.")

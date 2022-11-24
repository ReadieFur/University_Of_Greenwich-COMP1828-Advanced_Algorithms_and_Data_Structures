from typing import Dict, List
from sys import maxsize as INT_MAX
from tubemap.core.tubemap_graph import TubemapGraph
from tubemap.core.tubemap_node import TubemapNode
from algorithms.algorithm import AlgorithmNode, PathPart
from algorithms.bellman_fords_algorithm_dp import BellmanFordsAlgorithmDP

class TubemapBellmanFordNode(AlgorithmNode):
    @property
    def node(self) -> TubemapNode:
        return super().node

    def __init__(self, node: TubemapNode) -> None:
        super().__init__(node)

class TubemapBellmanFordsAlgorithmDP(BellmanFordsAlgorithmDP):
    @staticmethod
    def find_shortest_path(graph: TubemapGraph, start_node: TubemapNode, end_node: TubemapNode) -> List[PathPart]:
        bellman_ford_nodes: Dict[int, AlgorithmNode] = {}

        #Set all distances to MAX_INT and the start node to 0.
        for node in graph.nodes.values():
            bellman_ford_nodes[node.id] = AlgorithmNode(node)
        bellman_ford_nodes[start_node.id].path_weight = 0

        #Relax all edges |V| - 1 times.
        #Relaxing an edge is when we check the currently processed nodes to see if there is a shorter path than the current one.
        for _ in range(len(graph.nodes) - 1):
            for [source, destination, edge] in graph.edge_list.values():
                if not edge.closed and bellman_ford_nodes[source.id].path_weight != INT_MAX and bellman_ford_nodes[source.id].path_weight + edge.weight < bellman_ford_nodes[destination.id].path_weight:
                    bellman_ford_nodes[destination.id].path_weight = bellman_ford_nodes[source.id].path_weight + edge.weight
                    bellman_ford_nodes[destination.id].previous_node = bellman_ford_nodes[source.id]
                    bellman_ford_nodes[destination.id].previous_edge = edge

        #Check for negative-weight cycles.
        #Negative weight cycles are when a path is found that is shorter than the current one, this will result in an infinite loop.
        for [source, destination, edge] in graph.edge_list.values():
            if bellman_ford_nodes[source.id].path_weight != INT_MAX and bellman_ford_nodes[source.id].path_weight + edge.weight < bellman_ford_nodes[destination.id].path_weight:
                raise RecursionError("Negative weight cycle detected.")

        #Return the shortest path.
        return AlgorithmNode.to_path_array(bellman_ford_nodes[end_node.id])

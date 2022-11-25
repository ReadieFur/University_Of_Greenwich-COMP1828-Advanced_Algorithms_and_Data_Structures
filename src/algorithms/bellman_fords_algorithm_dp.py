from typing import Dict, List
from sys import maxsize as INT_MAX
from algorithms.algorithm import AAlgorithm, AlgorithmNode, PathPart
from core.graph import Graph
from core.node import Node

"""
* I am using the following psuedocode to assist in my creation of this algorithm:
* From: COMP1828 "Dynamic Programming 2.pptx" slide 20:
# Input: A weighted connected graph G = (V, E) with nonnegative weights and its vertex s
# Output: The length dist(s, v) of a shortest path from s to v and its penultimate vertex pv for every vertex v in V.
# d(i, v): The distance of a shortest path from s to v given edge budget i.
ALGORITHM Bellman-Ford-DynPrg(G, s)
    Initalize(G, s): #initalize
    for i < 1 to |V| - 1 do
        for each vertex v do
            d(i, v) <- d(i - 1, v) #case 1
            for each incoming edge (u, v) do
                d(i, v) <- mi{d(i, v), d(i - 1, u) + w(u, v)} #case 2
    #... check for a negitive-weiht cycle
    for each vertex v do
        dist(s, v) <- d(|V| - 1, v)
"""
#The psuedocode above I found harder to understand and didn't have as much time as I would've liked to understand it so I am modifying from the C# (I understand C# better than Python, hence I'm using that example) source on GeeksForGeeks: https://www.geeksforgeeks.org/bellman-ford-algorithm-dp-23/
class BellmanFordsAlgorithmDP(AAlgorithm):
    @staticmethod
    def find_shortest_path(graph: Graph, start_node: Node, end_node: Node) -> List[PathPart]:
        bellman_ford_nodes: Dict[int, AlgorithmNode] = {}

        #Set all distances to MAX_INT and the start node to 0.
        for node in graph.nodes.values():
            bellman_ford_nodes[node.id] = AlgorithmNode(node)
        bellman_ford_nodes[start_node.id].path_weight = 0

        #Relax all edges |V| - 1 times.
        #Relaxing an edge is when we check the currently processed nodes to see if there is a shorter path than the current one.
        for _ in range(len(graph.nodes) - 1):
            #In the example they iterate over all of the edges in the graph, however I've noticed that they look at the source edge and then the destination edge of each recorded edge, this only works one way meaning the reason my tests may have failed is becuase a shorter path was valid in the other direction, but the algorithm never saw it, e.g. start at B and end at D, A-B=1, A-C=4, B-D=2, C-D=1, summarised, the example will get up to A=inf B=0 D=1 C=inf because when checking C-D, C is inf so it skips checking the weight and as it only checks source to dest, it will never see that D-C=1 where C=inf and D=1 meaning it won't update C's weight to 2.
            for [source, destination, edge] in graph.edge_list.values():
                if bellman_ford_nodes[source.id].path_weight != INT_MAX and bellman_ford_nodes[source.id].path_weight + edge.weight < bellman_ford_nodes[destination.id].path_weight:
                    bellman_ford_nodes[destination.id].path_weight = bellman_ford_nodes[source.id].path_weight + edge.weight
                    bellman_ford_nodes[destination.id].previous_node = bellman_ford_nodes[source.id]
                    bellman_ford_nodes[destination.id].previous_edge = edge
                elif bellman_ford_nodes[destination.id].path_weight != INT_MAX and bellman_ford_nodes[destination.id].path_weight + edge.weight < bellman_ford_nodes[source.id].path_weight:
                    bellman_ford_nodes[source.id].path_weight = bellman_ford_nodes[destination.id].path_weight + edge.weight
                    bellman_ford_nodes[source.id].previous_node = bellman_ford_nodes[destination.id]
                    bellman_ford_nodes[source.id].previous_edge = edge

        #Check for negative-weight cycles.
        #Negative weight cycles are when a path is found that is shorter than the current one, this will result in an infinite loop.
        for [source, destination, edge] in graph.edge_list.values():
            if bellman_ford_nodes[source.id].path_weight != INT_MAX and bellman_ford_nodes[source.id].path_weight + edge.weight < bellman_ford_nodes[destination.id].path_weight or bellman_ford_nodes[destination.id].path_weight != INT_MAX and bellman_ford_nodes[destination.id].path_weight + edge.weight < bellman_ford_nodes[source.id].path_weight:
                raise RecursionError("Negative weight cycle detected.")

        #Return the shortest path.
        return AlgorithmNode.to_path_array(bellman_ford_nodes[end_node.id])

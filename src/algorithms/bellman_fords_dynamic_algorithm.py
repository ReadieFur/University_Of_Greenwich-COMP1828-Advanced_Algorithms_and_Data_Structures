from algorithms.algorithm import AAlgorithm
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
class BellmanFordsDynamicAlgorithm(AAlgorithm):
    @staticmethod
    def find_shortest_path(start_node: Node, end_node: Node, graph: Graph):
        pass

from typing import List
from algorithms.algorithm import AAlgorithm, PathPart
from core.graph import Graph
from core.node import Node

"""
* I am using the following psuedocode to assist in my creation of this algorithm:
* From: COMP1828 "Dynamic Programming 2.pptx" slide 13 and 14:
Relax(u, v, w):
    if du + w(u, v) < dv
        dv <- du + w(u, v)
        pv <- u

# Input: A weighted connected graph G = (V, E) with nonnegative weights and its vertex s
# Output: The length dv of a shortest path from s to v and it's penultimate vertex pv for every vertex v in V
ALGORITHM Bellman-Ford(G, s)
    Initalize-Single-Source(G, s): #initalize
    for i < 1 to |V| - 1 do
        for each edge (u, v) do
            Relax(u, v, w)
    for each edge (u, v) do #check for a negitive-weiht cycle
        if du + w(u, v) < dv
            return false
    return true
"""
class BellmanFordsAlgorithm(AAlgorithm):
    @staticmethod
    def find_shortest_path(start_node: Node, end_node: Node, graph: Graph) -> List[PathPart]:
        pass

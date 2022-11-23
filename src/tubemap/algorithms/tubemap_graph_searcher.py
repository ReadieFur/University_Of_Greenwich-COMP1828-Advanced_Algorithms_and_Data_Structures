from typing import List
from tubemap.core.tubemap_graph import TubemapGraph
from tubemap.core.tubemap_node import TubemapNode

class TubemapGraphSearcher:
    @staticmethod
    def _breadth_first_search(graph: TubemapGraph, node: TubemapNode, visited: List[TubemapNode]) -> None:
        queue = [node]

        while len(queue) > 0:
            current = queue.pop(0)

            if current in visited:
                continue
            visited.append(current)

            for neibouring_node_id, edges in current.adjacency_dict.items():
                for edge in edges.values():
                    if edge.closed:
                        continue
                    queue.append(graph.nodes[neibouring_node_id])
                    #We only need to know if at least one open line exists to the node, so we can break out of the nested loop here.
                    break

    @staticmethod
    def is_path_available(graph: TubemapGraph, start: TubemapNode, end: TubemapNode) -> bool:
        visited: List[TubemapNode] = []

        TubemapGraphSearcher._breadth_first_search(graph, start, visited)

        return end in visited

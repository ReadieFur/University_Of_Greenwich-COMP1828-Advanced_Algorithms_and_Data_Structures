from typing import List
from tubemap.core.tubemap_node import TubemapNode

class TubemapGraphSearcher:
    @staticmethod
    def _breadth_first_search(node: TubemapNode, visited: List[TubemapNode]) -> None:
        queue = [node]

        while len(queue) > 0:
            current = queue.pop(0)

            if current in visited:
                continue
            visited.append(current)

            for neibouring_node, edge in current.adjacency_list.items():
                if edge.closed:
                    continue
                queue.append(neibouring_node)

    @staticmethod
    def is_path_available(start: TubemapNode, end: TubemapNode) -> bool:
        visited: List[TubemapNode] = []

        TubemapGraphSearcher._breadth_first_search(start, visited)

        return end in visited

from .dijkstras_algorithm import DijkstrasAlgorithm
from core.graph import Graph

class AlgorithmTests:
    def run() -> None:
        AlgorithmTests._test1()

    def _test1() -> None:
        """
        From the example: COMP1828 "Graph 1.pptx" slide 33
        Find the shortest path from node A to G.
        Expect the path to be A  -> B -> D -> E -> G.
        """

        graph = Graph()
        a = graph.add_node()
        b = graph.add_node()
        c = graph.add_node()
        d = graph.add_node()
        e = graph.add_node()
        f = graph.add_node()
        g = graph.add_node()

        graph.add_edge(a, b, 4)
        graph.add_edge(a, c, 3)
        graph.add_edge(b, d, 1)
        graph.add_edge(b, f, 4)
        graph.add_edge(c, d, 3)
        graph.add_edge(c, e, 5)
        graph.add_edge(d, e, 2)
        graph.add_edge(d, f, 2)
        graph.add_edge(d, g, 7)
        graph.add_edge(e, g, 2)
        graph.add_edge(f, g, 4)

        LABELS = {
            a: "A",
            b: "B",
            c: "C",
            d: "D",
            e: "E",
            f: "F",
            g: "G"
        }

        """
              B -----(4)----- F
             / \            / |
           (4)  -(1)-   -(2)  |
           /         \ /      |
          A ---(7)--- D ---  (4)
           \          |    \  |
           (3)       (2)   (7)|
             \        |      \|
              C -(5)- E -(2)- G
        """

        expected_result = ["A", "B", "D", "E", "G"]
        shortest_path = [LABELS[node] for node in DijkstrasAlgorithm.dijkstra_node_to_node_array(DijkstrasAlgorithm.find_shortest_path(graph, a, g))]
        print("Expected result: " + str(expected_result), end=", ")
        print("Actual result: " + str(shortest_path), end=", ")
        print("Test passed: " + str(expected_result == shortest_path))

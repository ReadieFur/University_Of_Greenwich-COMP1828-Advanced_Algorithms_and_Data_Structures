from .graph_searcher import GraphSearcher
from .dijkstras_algorithm import DijkstrasAlgorithm
from core.graph import Graph

class _GraphSearcherTests:
    @staticmethod
    def run() -> None:
        _GraphSearcherTests._test1()
        _GraphSearcherTests._test2()

    @staticmethod
    def _test1() -> None:
        print(_GraphSearcherTests._test1.__name__)

        graph = Graph()

        node1 = graph.add_node()
        node2 = graph.add_node()
        node3 = graph.add_node()
        node4 = graph.add_node()

        graph.add_edge(node1, node2, 1)
        graph.add_edge(node1, node3, 1)
        graph.add_edge(node2, node4, 1)

        print("BFS", GraphSearcher.is_graph_connected(graph, True)); #True
        print("DFS", GraphSearcher.is_graph_connected(graph, False)) #True

    @staticmethod
    def _test2() -> None:
        print(_GraphSearcherTests._test1.__name__)

        graph = Graph()

        node1 = graph.add_node()
        node2 = graph.add_node()
        node3 = graph.add_node()
        node4 = graph.add_node()

        graph.add_edge(node1, node2, 1)
        graph.add_edge(node1, node3, 1)
        # graph.add_edge(node2, node4, 1)

        print("BFS", GraphSearcher.is_graph_connected(graph, True)); #False
        print("DFS", GraphSearcher.is_graph_connected(graph, False)) #False

class _DijkstrasAlgorithmTests:
    @staticmethod
    def run() -> None:
        _DijkstrasAlgorithmTests._test1()
        _DijkstrasAlgorithmTests._test2()

    @staticmethod
    def _test1() -> None:
        print(_DijkstrasAlgorithmTests._test1.__name__)

        graph = Graph()

        a = graph.add_node()
        b = graph.add_node()
        c = graph.add_node()
        d = graph.add_node()

        graph.add_edge(a, b, 1)
        graph.add_edge(a, c, 4)
        graph.add_edge(b, d, 2)
        graph.add_edge(c, d, 1)

        LABELS = {
            a: "A",
            b: "B",
            c: "C",
            d: "D"
        }

        """
              B
             / \
           (1) (2)
           /     \
          A       D
           \     /
           (4) (1)
             \ /
              C
        """

        #Expected shortest path from A to D is A -> B -> D.
        expected_result = ["A", "B", "D"]
        shortest_path = [LABELS[node] for node in DijkstrasAlgorithm.dijkstra_node_to_node_array(DijkstrasAlgorithm.find_shortest_path(graph, a, d))]
        print("Expected result: " + str(expected_result), end=", ")
        print("Actual result: " + str(shortest_path), end=", ")
        print("Test passed: " + str(expected_result == shortest_path))

    @staticmethod
    def _test2() -> None:
        print(_DijkstrasAlgorithmTests._test2.__name__)

        graph = Graph()

        a = graph.add_node()
        b = graph.add_node()
        c = graph.add_node()
        d = graph.add_node()
        e = graph.add_node()
        f = graph.add_node()
        g = graph.add_node()

        #From the example: COMP1828 "Graph 1.pptx" slide 33
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

        #Expected shortest path from A to G is A -> B -> D -> E -> G.
        expected_result = ["A", "B", "D", "E", "G"]
        shortest_path = [LABELS[node] for node in DijkstrasAlgorithm.dijkstra_node_to_node_array(DijkstrasAlgorithm.find_shortest_path(graph, a, g))]
        print("Expected result: " + str(expected_result), end=", ")
        print("Actual result: " + str(shortest_path), end=", ")
        print("Test passed: " + str(expected_result == shortest_path))

class AlgorithmTests:
    @staticmethod
    def run() -> None:
        _GraphSearcherTests.run()
        _DijkstrasAlgorithmTests.run()
